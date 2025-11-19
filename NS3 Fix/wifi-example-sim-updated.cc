/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Authors: Joe Kopena <tjkopena@cs.drexel.edu>
 * Modified by: Longhao Zou, Oct 2016 for EE500 <longhao.zou@dcu.ie>
 *

            EE500 Assignment 2016-2017
            Default WiFi Network Topology

                WiFi 192.168.0.0
            -------------------------
            |AP(node 0:192.168.0.1)|
            -------------------------
             *         *           *
            /          |            \
  Traffic 1/  Traffic 2|    ------   \ Traffic N
          /            |              \
      user 1       user 2     ------   user N
  (node 1        (node 2     ------ (node N
   :192.168.0.2    :192.168.0.3 ------ :192.168.0.N+1
   :1000)          :1001)        ------:1000+(N-1))

   PS: In this example, I just implemented only 1 WiFi user.

 */

#include <ctime>
#include <iostream>

#include <sstream>

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/wifi-module.h"
#include "ns3/internet-module.h"

#include "ns3/stats-module.h"

#include "wifi-example-apps.h"
#include <vector>
#include <cmath>

using namespace ns3;
using namespace std;

NS_LOG_COMPONENT_DEFINE("WiFiExampleSim");




void TxCallback(Ptr<CounterCalculator<uint32_t> > datac, std::string path, Ptr<const Packet> packet) {
  NS_LOG_INFO("Sent frame counted in " << datac->GetKey());
  datac->Update();
  // end TxCallback
}




//----------------------------------------------------------------------
//-- main
//----------------------------------------------
int main(int argc, char *argv[]) {
  LogComponentEnable("WiFiExampleSim", LOG_LEVEL_INFO);

  std::cout << "Starting WiFi simulation..." << std::endl;

  // Simulation parameters
  double simTime = 20; // Simulation Running Time(in seconds)
  double bitRate = 5000; // 5 Mbps for Question C
  std::string format = "omnet"; // Default as Omnet format

  // Identifiers
  string experiment("wifi-example-sim"); //the name of your experiment
  string strategy("wifi-default");
  string input;
  string runID;

  // Question C Parameters
  std::vector<int> userCounts = {1, 10, 20, 50};
  std::vector<double> distances = {0.0, 30.0, 60.0, 90.0, 120.0, 150.0};
  std::vector<std::pair<std::string, WifiStandard>> wifiStandards = {
    {"WiFi6_80211ax", WIFI_STANDARD_80211ax},
    {"WiFi7_80211be", WIFI_STANDARD_80211be}
  };

  Ptr<DataOutputInterface> output = CreateObject<OmnetDataOutput>();


  {
    stringstream sstr;
    sstr << "run-" << time(NULL);
    runID = sstr.str();
  }

  // Generate unique run number
  uint32_t baseRunNumber = time(NULL);
  uint32_t runCounter = 0;

  for( auto [stdName, stdType] : wifiStandards ) {
    std::cout << "Testing standard: " << stdName << std::endl;

    for(double distance : distances) {
      for(int users : userCounts){
        std::cout << "  Distance: " << distance << "m, Users: " << users << std::endl;

        // Create Nodes(1 AP + N users)
        NodeContainer nodes;
        nodes.Create(users + 1); // +1 for AP

        // Install WiFi
        WifiHelper wifi;
        wifi.SetStandard(stdType);
        wifi.SetRemoteStationManager("ns3::MinstrelHtWifiManager");

        WifiMacHelper wifiMac;
        wifiMac.SetType("ns3::AdhocWifiMac");

        YansWifiPhyHelper wifiPhy; // Line changed as no need for constructor here
        YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
        wifiPhy.SetChannel(wifiChannel.Create());


        wifiPhy.Set("TxPowerStart", DoubleValue(40.0)); // default was 16.0
        wifiPhy.Set("TxPowerEnd", DoubleValue(40.0));
        wifiPhy.Set("RxSensitivity", DoubleValue(-96.0)); // dBm(more sensitive)

        NetDeviceContainer nodeDevices = wifi.Install(wifiPhy, wifiMac, nodes);
        std::cout << "WiFi devices installed successfully." << std::endl;

        // Internet Setup
        InternetStackHelper internet;
        internet.Install(nodes);

        Ipv4AddressHelper ipAddrs;
        ipAddrs.SetBase("192.168.0.0", "255.255.255.0");
        ipAddrs.Assign(nodeDevices);

        //Node Positions
        MobilityHelper mobility;
        Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator>();
        positionAlloc->Add(Vector(0.0, 0.0, 0.0)); // AP position

        for(int i = 1; i <= users; ++i) {
          if(users ==1){
            positionAlloc->Add(Vector(0.0, distance, 0.0)); // User positions
            }
            else{
          // Multiple users: distribute them in a circle around the AP
            double angle = 2.0 * M_PI * (i - 1) / users; // Evenly distribute around circle
            double x = distance * cos(angle);
            double y = distance * sin(angle);
            positionAlloc->Add(Vector(x, y, 0.0));
          }
        } 

        mobility.SetPositionAllocator(positionAlloc);
        mobility.Install(nodes);

        // Traffic Setup
        std::vector<Ptr<Receiver>> receivers; // Store receivers for data collection

        for(int i = 1; i<=users; ++i){
          Ptr<Receiver> receiver = CreateObject<Receiver>();
          // Sender(AP to User i)
          Ptr<Node> appSource = nodes.Get(0);
          Ptr<Node> appSink   = nodes.Get(i);


          Ptr<Sender> sender = CreateObject<Sender>();
          sender->SetAttribute("Port", UintegerValue(1000 + i)); //Listening Port of the WiFi user
          sender->SetAttribute("PacketSize", UintegerValue(1000)); //bytes

          double bitsPerPacket = 1000 * 8; // Convert bytes to bits
          double bitRateBps = bitRate * 1000; // Convert Kbps to
          double transmissionInterval = bitsPerPacket / bitRateBps; // seconds between packets

          std::stringstream intervalStream;
          intervalStream << "ns3::ConstantRandomVariable[Constant=" << transmissionInterval << "]";
          sender->SetAttribute("Interval", StringValue(intervalStream.str())); //seconds
          sender->SetAttribute("NumPackets",UintegerValue(100000000));

          appSource->AddApplication(sender);
          sender->SetStartTime(Seconds(0));

          // Receiver(User i)
          receiver->SetAttribute("Port", UintegerValue(1000 + i)); //Listening Port
          appSink->AddApplication(receiver);
          receiver->SetStartTime(Seconds(0));
          receivers.push_back(receiver); // Store for data collection

          // Set Destination
          std::stringstream dest;
          dest << "192.168.0." <<(i + 1);
          std::string destStr = "/NodeList/0/ApplicationList/" + std::to_string(i-1) + "/$Sender/Destination";
          Config::Set(destStr, Ipv4AddressValue(dest.str().c_str()));
        }

        // Data Collection Setup for each receiver.
        DataCollector dataCollector;
        std::stringstream inputStream;
        inputStream << "dist" << distance << "_users" << users << "_" << stdName;
        dataCollector.DescribeRun(experiment, strategy, inputStream.str(), runID);
        dataCollector.AddMetadata("author", "EEN1058-KYLE-SHEEHY");
        
        // WiFi frame counters
        Ptr<CounterCalculator<uint32_t>> totalTx = CreateObject<CounterCalculator<uint32_t>>();
        totalTx->SetKey("wifi-tx-frames");
        totalTx->SetContext("node[0]");
        Config::Connect("/NodeList/0/DeviceList/*/$ns3::WifiNetDevice/Mac/MacTx",
                         MakeBoundCallback(&TxCallback, totalTx));
        dataCollector.AddDataCalculator(totalTx);

        for(int i=1; i<=users; ++i){
          Ptr<PacketCounterCalculator> totalRx = CreateObject<PacketCounterCalculator>();
          totalRx->SetKey("wifi-rx-frames");
          std::stringstream context;
          context << "node[" << i << "]";
          totalRx->SetContext(context.str());

          std::stringstream Path;
          Path << "/NodeList/" << i << "/DeviceList/*/$ns3::WifiNetDevice/Mac/MacRx";
          Config::Connect(Path.str(), MakeCallback(&PacketCounterCalculator::PacketUpdate,totalRx));
          dataCollector.AddDataCalculator(totalRx);
        }

        // Application level counters
        for(int i =0; i<users; ++i){
          // Tx packets
          Ptr<PacketCounterCalculator> appTx = CreateObject<PacketCounterCalculator>();
          appTx->SetKey("sender-tx-packets");
          appTx->SetContext("node[0]");
          std::stringstream txPath;
          txPath << "/NodeList/0/ApplicationList/" << i << "/$Sender/Tx";
          Config::Connect(txPath.str(), MakeCallback(&PacketCounterCalculator::PacketUpdate,appTx));
          dataCollector.AddDataCalculator(appTx);

          // Rx packets
          Ptr<CounterCalculator<> > appRx = CreateObject<CounterCalculator<> >();
          appRx->SetKey("receiver-rx-packets");
          std::stringstream rxContext;
          rxContext << "node[" << (i + 1) << "]";
          appRx->SetContext(rxContext.str());
          receivers[i]->SetCounter(appRx);
          dataCollector.AddDataCalculator(appRx);

          // Delay tracking
          Ptr<TimeMinMaxAvgTotalCalculator> delayStat = CreateObject<TimeMinMaxAvgTotalCalculator>();
          delayStat->SetKey("delay");
          delayStat->SetContext(".");
          receivers[i]->SetDelayTracker(delayStat); //nanoseconds
          dataCollector.AddDataCalculator(delayStat);
        }
        
        // Run Simulation
        Simulator::Stop(Seconds(simTime));
        Simulator::Run();

        // Generate Output
        std::stringstream fileNameBuilder;
        fileNameBuilder << "DataOfUser1-" << runID << "-" << (int)distance << "m-" << users << "users-" << stdName;
        std::string filePrefix = fileNameBuilder.str();
        output->SetFilePrefix(filePrefix);
        output->Output(dataCollector);


        // Output message per run
        std::cout << "  Output saved: '" << filePrefix << "'.sca" << std::endl;
        Simulator::Destroy();
        receivers.clear(); // Clear receivers for next run
        }
      }
      std::cout << "WiFi standard " << stdName << " testing completed." << std::endl;
    }
    return 0;
  }

  

  // // Set up command line parameters used to control the experiment.
  // CommandLine cmd;
  // cmd.AddValue("distance", "Distance apart to place nodes(in meters).",
  //               distance);
  // cmd.AddValue("format", "Format to use for data output(omnet or db).",
  //               format);
  // cmd.AddValue("simTime", "Simulation Running Time(in seconds)", simTime);

  // cmd.AddValue("bitRate", "Target bit rate in Kbps ", bitRate); // Can change to 1,5,10Mbps per question

  // cmd.AddValue("experiment", "Identifier for experiment.",
  //               experiment);
  // cmd.AddValue("strategy", "Identifier for strategy.",
  //               strategy);
  // cmd.AddValue("run", "Identifier for run.",
  //               runID);
  // cmd.Parse(argc, argv);
  // if(bitRate > 0) {
  //   std::cout << "Command line arguments parsed. Distance: " << distance << "m, SimTime: " << simTime << "s, Format: " << format << ", BitRate: " << bitRate << " Kbps" << std::endl;
  // } else {
  //   std::cout << "Command line arguments parsed. Distance: " << distance << "m, SimTime: " << simTime << "s, Format: " << format << "(using default transmission interval)" << std::endl;
  // }

  // if(format != "omnet" && format != "db") {
  //     NS_LOG_ERROR("Unknown output format '" << format << "'");
  //     return -1;
  //   }

  // {
  //   stringstream sstr("");
  //   sstr << distance;
  //   input = sstr.str();
  // }




  // //------------------------------------------------------------
  // //-- Create nodes and network stacks
  // //--------------------------------------------
  // std::cout << "Creating nodes and network stacks..." << std::endl;
  // NS_LOG_INFO("Creating nodes.");
  // NodeContainer nodes;
  // nodes.Create(2);
  // std::cout << "Created " << nodes.GetN() << " nodes." << std::endl;

  // NS_LOG_INFO("Installing WiFi and Internet stack.");
  // std::cout << "Setting up WiFi(802.11ax standard)..." << std::endl;
  // WifiHelper wifi;
  // // For Question C, try WIFI_PHY_STANDARD_80211be(WiFi 7) as well // Try to run with different WiFI standard like WIFI_PHY_STANDARD_80211ax(802.11ac operates in the 5Ghz range only, while 802.11ax operates in both the 2.4Ghz and 5Ghz ranges, thus creating more available channels. ... 802.11ax supports up to eight MU-MIMO transmissions at a time, up from four with 802.11ac)
  // wifi.SetStandard(WIFI_STANDARD_80211ax); // Default updated to WiFi 6(802.11ax)
  
  // wifi.SetRemoteStationManager("ns3::MinstrelHtWifiManager");
  // WifiMacHelper wifiMac;
  // wifiMac.SetType("ns3::AdhocWifiMac");
  // YansWifiPhyHelper wifiPhy; // Line changed as no need for constructor here
  // YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
  // wifiPhy.SetChannel(wifiChannel.Create());
  
  // // Increase TX power to support very long distances(up to ~200m)
  // wifiPhy.Set("TxPowerStart", DoubleValue(40.0)); // default was 16.0
  // wifiPhy.Set("TxPowerEnd", DoubleValue(40.0));   
  
  // // Also lower the receiver sensitivity threshold for better range
  // wifiPhy.Set("RxSensitivity", DoubleValue(-96.0)); // dBm(more sensitive)
  
  // NetDeviceContainer nodeDevices = wifi.Install(wifiPhy, wifiMac, nodes);
  // std::cout << "WiFi devices installed successfully." << std::endl;

  // InternetStackHelper internet;
  // internet.Install(nodes);
  // std::cout << "Internet stack installed." << std::endl;
  // Ipv4AddressHelper ipAddrs;
  // ipAddrs.SetBase("192.168.0.0", "255.255.255.0");
  // ipAddrs.Assign(nodeDevices);
  // std::cout << "IP addresses assigned(192.168.0.0)." << std::endl;

  // //------------------------------------------------------------
  // //-- Setup physical layout
  // //--------------------------------------------
  // std::cout << "Setting up physical layout with distance: " << distance << "m" << std::endl;
  // NS_LOG_INFO("Installing static mobility; distance " << distance << " .");
  // MobilityHelper mobility;
  // Ptr<ListPositionAllocator> positionAlloc =
  //   CreateObject<ListPositionAllocator>();
  // positionAlloc->Add(Vector(0.0, 0.0, 0.0));
  // positionAlloc->Add(Vector(0.0, distance, 0.0));
  // mobility.SetPositionAllocator(positionAlloc);
  // mobility.Install(nodes);
  // std::cout << "Mobility model installed. Node positions set." << std::endl;


  // //------------------------------------------------------------
  // //-- Create the traffic between AP and WiFi Users
  // //------------------------------------------------------------
  // //------------------------------------------------------------
  // //-- 1. Create the first traffic for the first WiFi user on WiFi AP(source)
  // //--------------------------------------------
  // std::cout << "Creating traffic applications..." << std::endl;
  // NS_LOG_INFO("Create traffic source & sink.");
  
  // Ptr<Node> appSource = NodeList::GetNode(0);
  // Ptr<Sender> sender = CreateObject<Sender>();
  // sender->SetAttribute("Port", UintegerValue(1000));//Listening Port of the first WiFi user
  
  // uint32_t packetSize = 1000; // bytes
  // sender->SetAttribute("PacketSize", UintegerValue(packetSize)); //bytes
  
  // // Configure transmission interval based on whether bit rate is specified
  // if(bitRate > 0) {
  //   // Calculate transmission interval based on desired bit rate
  //   double bitsPerPacket = packetSize * 8; // Convert bytes to bits
  //   double bitRateBps = bitRate * 1000; // Convert Kbps to bps
  //   double transmissionInterval = bitsPerPacket / bitRateBps; // seconds between packets
    
  //   std::cout << "Configuring traffic for target bit rate: " << bitRate << " Kbps" << std::endl;
  //   std::cout << "Packet size: " << packetSize << " bytes, Transmission interval: " << transmissionInterval << " seconds" << std::endl;
    
  //   // Set transmission interval based on calculated value
  //   std::stringstream intervalStream;
  //   intervalStream << "ns3::ConstantRandomVariable[Constant=" << transmissionInterval << "]";
  //   sender->SetAttribute("Interval", StringValue(intervalStream.str())); //seconds
  // } else {
  //   // Use default transmission interval(original behavior)
  //   std::cout << "Using default transmission interval: 0.05 seconds(160 Kbps theoretical)" << std::endl;
  //   sender->SetAttribute("Interval", StringValue("ns3::ConstantRandomVariable[Constant=0.05]")); //seconds
  // }
  
  // sender->SetAttribute("NumPackets",UintegerValue(100000000));
  // appSource->AddApplication(sender);
  // sender->SetStartTime(Seconds(0));
  // std::cout << "Sender application created on node 0(port 1000)." << std::endl;

  // //------------------------------------------------------------
  // //-- 2. Create the first WiFi User(sink)
  // //--------------------------------------------
  // Ptr<Node> appSink = NodeList::GetNode(1);
  // Ptr<Receiver> receiver = CreateObject<Receiver>();
  // receiver->SetAttribute("Port", UintegerValue(1000));//Lisening Port
  // appSink->AddApplication(receiver);
  // receiver->SetStartTime(Seconds(0));
  // std::cout << "Receiver application created on node 1(port 1000)." << std::endl;

  // //Set IP address of the first User to AP(source)
  // Config::Set("/NodeList/*/ApplicationList/*/$Sender/Destination",
  //              Ipv4AddressValue("192.168.0.2"));
  // std::cout << "Traffic destination set to 192.168.0.2" << std::endl;




  // //------------------------------------------------------------
  // //-- Setup stats and data collection
  // //--  for the WiFi AP and the first WiFi User
  // //--------------------------------------------
  // // std::cout << "Setting up statistics and data collection..." << std::endl;

  // // Create a DataCollector object to hold information about this run.
  // DataCollector dataofuser1;
  // dataofuser1.DescribeRun(experiment,
  //                   strategy,
  //                   input,
  //                   runID);

  // // Add any information we wish to record about this run.
  // dataofuser1.AddMetadata("author", "EEN1058-KYLE-SHEEHY"); //Please replace XXX with your first name!


  // // Create a counter to track how many frames are generated.  Updates
  // // are triggered by the trace signal generated by the WiFi MAC model
  // // object.  Here we connect the counter to the signal via the simple
  // // TxCallback() glue function defined above.
  // Ptr<CounterCalculator<uint32_t> > totalTx =
  //   CreateObject<CounterCalculator<uint32_t> >();
  // totalTx->SetKey("wifi-tx-frames");
  // totalTx->SetContext("node[0]");
  // Config::Connect("/NodeList/0/DeviceList/*/$ns3::WifiNetDevice/Mac/MacTx",
  //                  MakeBoundCallback(&TxCallback, totalTx));
  // dataofuser1.AddDataCalculator(totalTx);

  // // This is similar, but creates a counter to track how many frames
  // // are received.  Instead of our own glue function, this uses a
  // // method of an adapter class to connect a counter directly to the
  // // trace signal generated by the WiFi MAC.
  // Ptr<PacketCounterCalculator> totalRx =
  //   CreateObject<PacketCounterCalculator>();
  // totalRx->SetKey("wifi-rx-frames");
  // totalRx->SetContext("node[1]");
  // Config::Connect("/NodeList/1/DeviceList/*/$ns3::WifiNetDevice/Mac/MacRx",
  //                  MakeCallback(&PacketCounterCalculator::PacketUpdate,
  //                                totalRx));
  // dataofuser1.AddDataCalculator(totalRx);




  // // This counter tracks how many packets---as opposed to frames---are
  // // generated.  This is connected directly to a trace signal provided
  // // by our Sender class.
  // Ptr<PacketCounterCalculator> appTx =
  //   CreateObject<PacketCounterCalculator>();
  // appTx->SetKey("sender-tx-packets");
  // appTx->SetContext("node[0]");
  // Config::Connect("/NodeList/0/ApplicationList/*/$Sender/Tx",
  //                  MakeCallback(&PacketCounterCalculator::PacketUpdate,
  //                                appTx));
  // dataofuser1.AddDataCalculator(appTx);

  // // Here a counter for received packets is directly manipulated by
  // // one of the custom objects in our simulation, the Receiver
  // // Application.  The Receiver object is given a pointer to the
  // // counter and calls its Update() method whenever a packet arrives.
  // Ptr<CounterCalculator<> > appRx =
  //   CreateObject<CounterCalculator<> >();
  // appRx->SetKey("receiver-rx-packets");
  // appRx->SetContext("node[1]");
  // receiver->SetCounter(appRx);
  // dataofuser1.AddDataCalculator(appRx);




  // /**
  //  * Just to show this is here...
  //  Ptr<MinMaxAvgTotalCalculator<uint32_t> > test =
  //  CreateObject<MinMaxAvgTotalCalculator<uint32_t> >();
  //  test->SetKey("test-dc");
  //  data.AddDataCalculator(test);

  //  test->Update(4);
  //  test->Update(8);
  //  test->Update(24);
  //  test->Update(12);
  // **/

  // // This DataCalculator connects directly to the transmit trace
  // // provided by our Sender Application.  It records some basic
  // // statistics about the sizes of the packets received(min, max,
  // // avg, total # bytes), although in this scenaro they're fixed.
  // Ptr<PacketSizeMinMaxAvgTotalCalculator> appTxPkts =
  //   CreateObject<PacketSizeMinMaxAvgTotalCalculator>();
  // appTxPkts->SetKey("tx-pkt-size");
  // appTxPkts->SetContext("node[0]");
  // Config::Connect("/NodeList/0/ApplicationList/*/$Sender/Tx",
  //                  MakeCallback
  //                   (&PacketSizeMinMaxAvgTotalCalculator::PacketUpdate,
  //                    appTxPkts));
  // dataofuser1.AddDataCalculator(appTxPkts);


  // // Here we directly manipulate another DataCollector tracking min,
  // // max, total, and average propagation delays.  Check out the Sender
  // // and Receiver classes to see how packets are tagged with
  // // timestamps to do this.
  // Ptr<TimeMinMaxAvgTotalCalculator> delayStat =
  //   CreateObject<TimeMinMaxAvgTotalCalculator>();
  // delayStat->SetKey("delay");
  // delayStat->SetContext(".");
  // receiver->SetDelayTracker(delayStat); //nanoseconds
  // dataofuser1.AddDataCalculator(delayStat);
  // std::cout << "All data calculators configured successfully." << std::endl;




  // //------------------------------------------------------------
  // //-- Run the simulation
  // //--------------------------------------------
  // NS_LOG_INFO("Run Simulation.");
  // std::cout << "Starting simulation run for " << simTime << " seconds..." << std::endl;
  // Simulator::Stop(Seconds(simTime));
  // Simulator::Run();
  // std::cout << "Simulation completed successfully!" << std::endl;




  // //------------------------------------------------------------
  // //-- Generate statistics output.
  // //--------------------------------------------
  // std::cout << "Generating statistics output..." << std::endl;
  // std::cout << "Using output format: " << format << std::endl;

  // Pick an output writer based in the requested format.
  // Ptr<DataOutputInterface> output = 0;
  // if(format == "omnet") {
  //     NS_LOG_INFO("Creating omnet formatted data output.");
  //     std::cout << "Creating Omnet++ format output writer..." << std::endl;
  //     output = CreateObject<OmnetDataOutput>();
  //   } else if(format == "db") {
  //     NS_LOG_INFO("Attempting to create sqlite formatted data output.");
  //     std::cout << "Trying to create SQLite database output writer..." << std::endl;
  //     try {
  //       output = CreateObject<SqliteDataOutput>();
  //       std::cout << "SQLite database output writer created successfully!" << std::endl;
  //     } catch(const std::exception& e) {
  //       std::cout << "Failed to create SQLite output writer: " << e.what() << std::endl;
  //       std::cout << "Falling back to Omnet format..." << std::endl;
  //       output = CreateObject<OmnetDataOutput>();
  //       format = "omnet";  // Update format for consistent behavior
  //     } catch(...) {
  //       std::cout << "Failed to create SQLite output writer(unknown error)" << std::endl;
  //       std::cout << "Falling back to Omnet format..." << std::endl;
  //       output = CreateObject<OmnetDataOutput>();
  //       format = "omnet";  // Update format for consistent behavior
  //     }
  //   } else {
  //     NS_LOG_ERROR("Unknown output format " << format);
  //   }

  // Finally, have that writer interrogate the DataCollector and save
  // the results.
  // I changed the file naming system so I can easily identify the files based on parameters given in cmd line
  // if(output != 0)
  // {
  //   // Create descriptive filename with timestamp and parameters
  //   std::stringstream fileNameBuilder;
  //   // Extract just the timestamp from runID 
  //   std::string timestamp = runID.substr(4); // Remove "run-" prefix
  //   //fileNameBuilder << "DataOfUser1-" << timestamp;
  //   fileNameBuilder << "DataOfUser1-"; // remove timestamp for easier file management

  //   // Add parameter-based suffix
  //   bool hasCustomParams = false;
    
  //   // Add bit rate if specified
  //   if(bitRate > 0) {
  //     fileNameBuilder << "-" <<(int)bitRate << "kbps";
  //     hasCustomParams = true;
  //   }
    
  //   // Add distance if not default(50m)
  //   if(distance != 50.0) {
  //     fileNameBuilder << "-" <<(int)distance << "m";
  //     hasCustomParams = true;
  //   }
    
  //   // Add simulation time if not default(20s)
  //   if(simTime != 20.0) {
  //     fileNameBuilder << "-" <<(int)simTime << "s";
  //     hasCustomParams = true;
  //   }
    
  //   // Add format if not default(omnet is default)
  //   if(format == "db") {
  //     fileNameBuilder << "-" << format;
  //     hasCustomParams = true;
  //   }
    
  //   // If no custom parameters, add "default"
  //   if(!hasCustomParams) {
  //     fileNameBuilder << "-default";
  //   }
    
  //   std::string filePrefix = fileNameBuilder.str();
    
  //   // Update the DataCollector with a clean runID to avoid duplication
  //   std::string originalRunID = runID;
  //   std::string cleanRunID = ""; // Empty to prevent automatic suffix
  //   dataofuser1.DescribeRun(experiment, strategy, input, cleanRunID);
    
  //   output->SetFilePrefix(filePrefix);
  //   output->Output(dataofuser1);
  //   std::cout << "Statistics output saved with prefix '" << filePrefix << "'." << std::endl;
  // } else {
  //   std::cout << "Warning: No output writer created, statistics not saved." << std::endl;
  // }
  // Free any memory here at the end of this example.

//   std::cout << "Cleaning up and destroying simulator..." << std::endl;
//   Simulator::Destroy();
//   std::cout << "WiFi simulation finished successfully!" << std::endl;

//   // end main
// }
