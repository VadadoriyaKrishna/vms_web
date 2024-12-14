from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

# System ips
tree = ET.parse('Configurations/all_configurations.xml')
root = tree.getroot()
system_ip = []
for elem in root:
    for subelem in elem:
        system_ip.append(subelem.text)

def trigger_no_connection_event(cam_id, target_ip=system_ip[2]):

    reference_no = "%02d" % cam_id + "%02d" % (29) + datetime.now().strftime("%d%m%y%H%M%S%f")[:14]
    update_database(target_ip = target_ip,
                    reference_no=reference_no, 
                    event_id = 30,
                    event_type =  2,
                    event_name = "Connection Error",
                    cam_id=cam_id
                   )

def update_database(target_ip, reference_no, event_id, event_type, event_name, cam_id):
    """
    :param reference_no:
    :param event_type: is it an alarm event?
    :param event_id: Identifier of the event
    :param event_name: Name of the event
    :param cam_id: Identifier of the camera/
    :return: None
    """
    
    timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

    event_data = {"Version": 2,
                    "ReferenceNo": reference_no,
                    "LocId": 1,
                    "SourceId": cam_id,
                    "EventCatId": event_id,
                    "EventValue": event_name,
                    "EventType": 2,
                    "ZoneId": 0,
                    "EventDate": timestamp,
                    "EventUrl": None,
                    "transfer_status": 0,
                    "VehicleClassId":1
                    }

    try:
        response = requests.post(target_ip, 
                                 data=event_data,
                                 timeout = 1
                                )
                                

        print("Response", response.status_code)
        
                            
    except Exception as e:
        print("Error in Sending. ERROR:", e)

    