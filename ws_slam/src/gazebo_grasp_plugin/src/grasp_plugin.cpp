// Gazebo World Plugin: attaches/detaches a block to the gripper via a fixed joint.
// Models a rigid grasp (what real friction does), avoiding Gazebo's weak grip friction.
#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <thread>

namespace gazebo
{
class GraspPlugin : public WorldPlugin
{
public:
  void Load(physics::WorldPtr _world, sdf::ElementPtr /*_sdf*/) override
  {
    this->world = _world;

    // Start ROS 2 if not already started
    if (!rclcpp::ok()) {
      rclcpp::init(0, nullptr);
    }
    this->ros_node = std::make_shared<rclcpp::Node>("gazebo_grasp_plugin");

    // Subscriber: /attach expects "gripper_link_model::link block_model"
    this->attach_sub = this->ros_node->create_subscription<std_msgs::msg::String>(
      "/attach", 10,
      std::bind(&GraspPlugin::OnAttach, this, std::placeholders::_1));

    this->detach_sub = this->ros_node->create_subscription<std_msgs::msg::String>(
      "/detach", 10,
      std::bind(&GraspPlugin::OnDetach, this, std::placeholders::_1));

    // Spin ROS in a background thread
    this->ros_thread = std::thread([this]() { rclcpp::spin(this->ros_node); });

    gzmsg << "[GraspPlugin] Loaded. Listening on /attach and /detach\n";
  }

  // Attach: create a fixed joint between the gripper link and the block
  void OnAttach(const std_msgs::msg::String::SharedPtr msg)
  {
    // message format: "robotModel::gripperLink blockModel"
    std::string data = msg->data;
    auto space = data.find(' ');
    std::string gripper_full = data.substr(0, space);   // robot::gripper_link
    std::string block_name = data.substr(space + 1);    // block model name

    auto robot_sep = gripper_full.find("::");
    std::string robot_model = gripper_full.substr(0, robot_sep);
    std::string gripper_link = gripper_full.substr(robot_sep + 2);

    physics::ModelPtr robot = this->world->ModelByName(robot_model);
    physics::ModelPtr block = this->world->ModelByName(block_name);
    if (!robot || !block) {
      gzerr << "[GraspPlugin] robot or block not found\n";
      return;
    }
    physics::LinkPtr glink = robot->GetLink(gripper_link);
    physics::LinkPtr blink = block->GetLink("link");
    if (!glink || !blink) {
      gzerr << "[GraspPlugin] gripper or block link not found\n";
      return;
    }

    // Create the fixed joint
    this->fixedJoint = this->world->Physics()->CreateJoint("fixed", robot);
    this->fixedJoint->Load(glink, blink, ignition::math::Pose3d());
    this->fixedJoint->Init();
    gzmsg << "[GraspPlugin] Attached " << block_name << " to " << gripper_link << "\n";
  }

  // Detach: remove the fixed joint
  void OnDetach(const std_msgs::msg::String::SharedPtr /*msg*/)
  {
    if (this->fixedJoint) {
      this->fixedJoint->Detach();
      this->fixedJoint.reset();
      gzmsg << "[GraspPlugin] Detached\n";
    }
  }

private:
  physics::WorldPtr world;
  physics::JointPtr fixedJoint;
  rclcpp::Node::SharedPtr ros_node;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr attach_sub;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr detach_sub;
  std::thread ros_thread;
};

GZ_REGISTER_WORLD_PLUGIN(GraspPlugin)
}  // namespace gazebo
