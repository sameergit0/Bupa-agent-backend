import os
from dotenv import load_dotenv
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Gemini API key not found")


add_note_declaration = {
    "name": "add_note",
    "description": "Adds a new note to the record of the currently logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "notes": {
                "type": "string",
                "description": "The full content of the note to be added."
            }
        },
        "required": ["notes"]
    }
}

disenroll_member_declaration = {
    "name": "disenroll_member",
    "description": "Removes the current logged-in member from the program. This tool requires a specific reason from a predefined list and a detailed note explaining the disenrollment.",
    "parameters": {
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "The specific reason for disenrollment.",
            },
            "disEnrollmentNote": {
                "type": "string",
                "description": "A detailed, free-form note providing more context and specifics about the disenrollment."
            }
        },
        "required": ["reason", "disEnrollmentNote"]
    }
}

add_health_metric_declaration = {
    "name": "add_health_metric",
    "description": "Records a specific health metric value for the current logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "metricsName": {
                "type": "string",
                "description": "The name of the health metric to be logged.",
            },
            "metricsVal": {
                "type": "number",
                "description": "The numerical value of the health metric.",
            },
            "metricsDate": {
                "type": "string",
                "description": "Date for which the metric should be logged, in 'YYYY-MM-DD' format.",
            }
        },
        "required": ["metricsName", "metricsVal", "metricsDate"]
    }
}

fetch_services_by_category_declaration = {
    "name": "services_by_category",
    "description": "Fetches a list of all available services that fall under a specific category.",
    "parameters": {
        "type": "object",
        "properties": {
            "categoryName": {
                "type": "string",
                "description": "The specific name of the service category to query.",
            }
        },
        "required": ["categoryName"]
    }
}

add_new_service_declaration = {
    "name": "add_new_service",
    "description": "Schedules a new service for the currently logged-in member under a specific category.",
    "parameters": {
        "type": "object",
        "properties": {
            "categoryName": {
                "type": "string",
                "description": "The category under which the new service falls."
            },
            "serviceName": {
                "type": "string",
                "description": "The specific name of the service to be scheduled."
            },
            "date": {
                "type": "string",
                "description": "Date for which the service should be scheduled, in 'YYYY-MM-DD' format."
            },
            "time": {
                "type": "string",
                "description": "Time for which the service should be scheduled, in 'HH:mm:ss' format."
            },
            "notes": {
                "type": "string",
                "description": "Optional, free-form notes to add details or special instructions for the service."
            }
        },
        "required": ["categoryName", "serviceName", "date", "time"]
    }
}

raise_new_ticket_declaration = {
    "name": "raise_new_ticket",
    "description": "Creates a new support ticket for the currently logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "A concise, single-line title summarizing the issue or request."
            },
            "ticketType": {
                "type": "string",
                "description": "The category or type of the ticket."
            },
            "priority": {
                "type": "string",
                "description": "The urgency level of the ticket, which must be chosen from a fixed list.",
                "enum": ["blocker", "major", "minor", "good_to_have"]
            },
            "description": {
                "type": "string",
                "description": "A detailed, free-form description of the issue."
            }
        },
        "required": ["title", "ticketType", "priority", "description"]
    }
}

fetch_program_details_declaration = {
    "name": "program_details",
    "description": "Fetches the complete hierarchy of all available programs, including their conditions and pathways.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

assign_program_declaration = {
    "name": "assign_program",
    "description": "Enrolls the current logged-in member in a new health program.",
    "parameters": {
        "type": "object",
        "properties": {
            "programName": {
                "type": "string",
                "description": "The name of the program to be assigned to the member."
            },
            "conditionName": {
                "type": "string",
                "description": "The name of the specific health condition or module within the program."
            },
            "pathwayName": {
                "type": "string",
                "description": "An optional, specific sub-pathway or track within the selected condition."
            }
        },
        "required": ["programName", "conditionName"]
    }   
}

fetch_user_assigned_programs_declaration = {
    "name": "user_assigned_programs",
    "description": "Fetches a list of all programs currently assigned to the logged-in member, including details on conditions, pathways, and their current status (active, stopped, notset).",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

stop_condition_declaration = {
    "name": "stop_condition",
    "description": "Stops an active condition or pathway for the currently logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "pathwayName": {
                "type": "string",
                "description": "The exact name of the pathway that belongs to the condition being stopped."
            },
            "remarks": {
                "type": "string",
                "description": "A detailed, free-form note explaining the reason for stopping the condition."
            }
        },
        "required": ["pathwayName", "remarks"]
    }   
}

restart_condition_declaration = {
    "name": "restart_condition",
    "description": "Restarts a previously stopped condition or pathway for the current logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "pathwayName": {
                "type": "string",
                "description": "The exact name of the pathway that belongs to the condition being restarted."
            },
            "remarks": {
                "type": "string",
                "description": "A detailed, free-form note explaining the reason for restarting the condition."
            }
        },
        "required": ["pathwayName", "remarks"]
    }
}

remove_condition_declaration = {
    "name": "remove_condition",
    "description": "Permanently removes a specific health condition, and its associated pathways, from the profile of the currently logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "conditionName": {
                "type": "string",
                "description": "The exact name of the condition to be removed from the member's profile."
            }
        },
        "required": ["conditionName"]
    }
}

fetch_available_pathways_for_program_condition_declaration = {
    "name": "available_pathways_for_program_condition",
    "description": "Fetches a list of all available pathways for a specific program and condition.",
    "parameters": {
        "type": "object",
        "properties": {
            "programName": {
                "type": "string",
                "description": "The exact name of the program for which to fetch pathways."
            },
            "conditionName": {
                "type": "string",
                "description": "The exact name of the condition within the specified program for which to fetch pathways."
            }
        },
        "required": ["programName", "conditionName"]
    }
}

change_pathway_declaration = {
    "name": "change_pathway",
    "description": "Changes the assigned pathway for the currently logged-in member within a specific program and condition.",
    "parameters": {
        "type": "object",
        "properties": {
            "programName": {
                "type": "string",
                "description": "The name of the program that contains the condition pathway to be changed."
            },
            "conditionName": {
                "type": "string",
                "description": "The name of the condition within the program whose pathway needs to be changed."
            },
            "oldPathwayName": {
                "type": "string",
                "description": "The name of the pathway currently assigned to the member that needs to be changed."
            },
            "newPathwayName": {
                "type": "string",
                "description": "The name of the new pathway to which the member's condition will be changed."
            },
            "notes": {
                "type": "string",
                "description": "An optional, free-form note explaining the reason for the pathway change."
            }
        },
        "required": ["programName", "conditionName", "oldPathwayName", "newPathwayName"]
    }
}

fetch_member_upcoming_scheduled_call_declaration = {
    "name": "member_upcoming_scheduled_call",
    "description": "Fetches the next upcoming scheduled call for the currently logged-in member. It returns the earliest scheduled call from the current date and time.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

cancel_or_reschedule_call_declaration = {
    "name": "cancel_or_reschedule_call",
    "description": "Modifies the next upcoming scheduled call for the logged-in member. `streamName` and `reasonForCancellation` both are different from each other ask for both.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "The desired action to perform: either 'cancel' or 're-schedule'.",
                "enum": ["cancel", "re-schedule"]
            },
            "old_slot_date": {
                "type": "string",
                "description": "The date of the appointment to be modified, in `DD MMM, YYYY` format (e.g., 10 Aug, 2025)."
            },
            "old_slot_time": {
                "type": "string",
                "description": "The time of the appointment to be modified, in `hh:mm am/pm` format (e.g., `07:00 am`)."
            },
            "new_slot": {
                "type": "string",
                "description": "The new date and time for the rescheduled call. Required if the action is 're-schedule'. Format should be 'YYYY-MM-DD HH:mm'."
            },
            "reasonForCancellation": {
                "type": "string",
                "description": "A free-form detailed note explaining the reason for canceling the call. Required if the action is 'cancel'."
            },
            "streamNames": {
                "type": "array",
                "description": "An array of strings for streams related to cancel the call. For example: ['Condition not covered', 'Member Deceased']. Required if the action is 'cancel'.",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["action", "old_slot_date", "old_slot_time"]
    }
}

fetch_available_tickets_declaration = {
    "name": "available_tickets",
    "description": "Fetches a comprehensive list of all support tickets currently associated with the logged-in member's profile.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

add_comment_on_ticket_declaration = {
    "name": "add_comment_on_ticket",
    "description": "Adds a new comment to an existing support ticket for the logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "ticketTitle": {
                "type": "string",
                "description": "The unique title of the support ticket to which the comment will be added.",
            },
            "comment": {
                "type": "string",
                "description": "The detailed, free-form text of the comment to be added to the ticket.",
            }
        },
        "required": ["ticketTitle", "comment"]
    }
}

fetch_lab_providers_declaration = {
    "name": "lab_providers",
    "description": "Retrieves a list of laboratory providers available in the specified city.",
    "parameters": {
        "type": "object",
        "properties": {
            "cityName": {
                "type": "string",
                "description": "The name of the city to search for laboratory providers.",
            }
        },
        "required": ["cityName"]
    }
}

lab_request_declaration = {
    "name": "lab_request",
    "description": "Submits a request to schedule a lab test for the current logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "coPayment": {
                "type": "string",
                "description": "Indicates whether a co-payment is required for the lab test.",
                "enum": ["yes", "no"]
            },
            "deductible": {
                "type": "string",
                "description": "The deductible amount in percentage. This parameter is only required and relevant if 'coPayment' is 'yes'.",
            },
            "preferredAppointmentDateTime": {
                "type": "string",
                "description": "The member's preferred date and time for the appointment. Format must be 'YYYY-MM-DD HH:mm'.",
            },
            "cityName": {
                "type": "string",
                "description": "The name of the city where the lab provider is located.",
            },
            "partnerClinic": {
                "type": "string",
                "description": "The name of the partner clinic where the lab test will be performed.",
            },
            "requestedLabTest": {
                "type": "array",
                "description": "An array of strings, each representing a lab test name. For example: ['151__HBA1c', '150__CBC'].",
                "items": {
                    "type": "string"
                }
            },
            "labProviderName": {
                "type": "string",
                "description": "The name of the lab provider.",
            },
            "district": {
                "type": "string",
                "description": "The optional district of the member."
            },
            "remarks": {
                "type": "string",
                "description": "Optional notes or additional remarks for the lab request."
            },
            "approvalNumber": {
                "type": "integer",
                "description": "An optional approval number for the request."
            }
        },
        "required": ["coPayment", "preferredAppointmentDateTime", "cityName", "partnerClinic", "requestedLabTest", "labProviderName"],
    }
}

fetch_homecare_lab_providers_declaration = {
    "name": "homecare_lab_providers",
    "description": "Retrieves a list of all available laboratory providers that offer home care services for a specific category in a given city.",
    "parameters": {
        "type": "object",
        "properties": {
            "cityName": {
                "type": "string",
                "description": "The name of the city where the home care lab providers are needed.",
            },
            "categoryName": {
                "type": "string",
                "description": "The name of the product category to search within.",
            }
        },
        "required": ["cityName", "categoryName"]
    }
}

fetch_homecare_health_products_declaration = {
    "name": "homecare_health_products",
    "description": "Retrieves a list of available home care health products for a specific category in a given city.",
    "parameters": {
        "type": "object",
        "properties": {
            "cityName": {
                "type": "string",
                "description": "The name of the city to search for home care health products.",
            },
            "categoryName": {
                "type": "string",
                "description": "The name of the product category to search within.",
            }
        },
        "required": ["cityName", "categoryName"]
    }
}

home_care_request_declaration = {
    "name": "home_care_request",
    "description": "Submits a request for a home care service or product for the current logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "coPayment": {
                "type": "string",
                "description": "Indicates whether a co-payment is required for the service.",
                "enum": ["yes", "no"]
            },
            "deductible": {
                "type": "string",
                "description": "The deductible amount in percentage. This parameter is only required and relevant if 'coPayment' is 'yes'.",
            },
            "preferredAppointmentDateTime": {
                "type": "string",
                "description": "The member's preferred date and time for the appointment. Format must be 'YYYY-MM-DD HH:mm'.",
            },
            "cityName": {
                "type": "string",
                "description": "The name of the city where the home care service or product is needed.",
            },
            "categoryName": {
                "type": "string",
                "description": "The name of the product category",
            },
            "labProviderName": {
                "type": "string",
                "description": "The name of the home care provider.",
            },
            "productName": {
                "type": "string",
                "description": "The name of the home care product.",
            },
            "district": {
                "type": "string",
                "description": "The optional district of the member."
            },
            "remarks": {
                "type": "string",
                "description": "Optional notes or additional remarks for the home care request."
            },
            "approvalNumber": {
                "type": "string",
                "description": "An optional approval number for the request.",
            }
        },
        "required": ["coPayment", "preferredAppointmentDateTime", "cityName", "categoryName", "labProviderName", "productName"],
    }
}

homebase_vaccine_request_declaration = {
    "name": "homebase_vaccine_request",
    "description": "Submits a request to schedule a vaccine service to be administered at the current logged-in member's home.",
    "parameters": {
        "type": "object",
        "properties": {
            "cityName": {
                "type": "string",
                "description": "The name of the city where the member is located.",
            },
            "productName": {
                "type": "string",
                "description": "The name of the home-base vaccine service package being requested.",
            },
            "deductible": {
                "type": "string",
                "description": "The coverage deductible amount in percentage for this request.",
            },
            "vaccine": {
                 "type": "string",
                "description": "The specific name of the vaccine to be administered",
            },
            "district": {
                "type": "string",
                "description": "The district within the city where the member is located."
            },
            "remarks": {
                "type": "string",
                "description": "Optional free-form notes or special instructions for the request."
            }
        },
        "required": ["cityName", "productName", "deductible", "vaccine", "district"]
    }
}

fetch_scheduled_calls_under_cn_declaration = {
    "name": "scheduled_calls_under_cn",
    "description": "Fetch all scheduled calls for members assigned to care navigator.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

fetch_userinfo_by_name_query_declaration = {
    "name": "userinfo_by_name_query",
    "description": "Searches for members under the current Care Navigator by a case-insensitive name or name prefix.",
    "parameters": {
        "type": "object",
        "properties": {
            "searchQuery": {
                "type": "string",
                "description": "A case-insensitive prefix of the member’s name to search for",
            }
        },
        "required": ["searchQuery"]
    }
}

schedule_call_with_cn_declaration = {
    "name": "schedule_call_with_cn",
    "description": "Schedules a new phone call between a specific member and their Care Navigator.",
    "parameters": {
        "type": "object",
        "properties": {
            "memberName": {
                "type": "string",
                "description": "The name of the member for whom the call appointment will be arranged.",
            },
            "appointmentDateTime": {
                "type": "string",
                "description": "The date and time of the appointment. Format must be `YYYY-MM-DD HH:mm:ss`.",
            },
        },
        "required": ["memberName", "appointmentDateTime"]
    }
}

fetch_member_profile_details_declaration = {
    "name": "member_profile_details",
    "description": "Fetches a comprehensive profile of the currently logged-in member. This includes personal information (e.g. name, age, city, mobile number), membership and contract details, health metrics (BMI, HBA1C), a list of all assigned programs, their conditions, and pathway statuses, and information about family members on the same policy.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

fetch_user_health_metric_data_declaration = {
    "name": "user_health_metric_data",
    "description": "Fetches historical and time-series data for a specific health metric for the currently logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "metricName": {
                "type": "string",
                "description": "The name of the health metric for which the data is required."
            }
        },
        "required": ["metricName"]
    }
}

fetch_member_notes_history_declaration = {
    "name": "member_notes_history",
    "description": "Fetches the complete history of all notes that have been added to the profile of the currently logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

fetch_member_journey_declaration = {
    "name": "member_journey",
    "description": "Fetches a complete, chronological 360° history of all key events and interactions for the currently logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

add_member_record_declaration = {
    "name": "add_member_record",
    "description": "Adds a new record to the health locker for the currently logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "reportType": {
                "type": "string",
                "description": "Category of the record to add.",
            },
            "description": {
                "type": "string",
                "description": "Free-text description for the new record."
            }
        },
        "required": ["reportType", "description"]
    }
}

fetch_health_locker_files_declaration = {
    "name": "health_locker_files",
    "description": "Fetches a list of files and documents from the currently logged-in member's health locker for a specified report category.",
    "parameters": {
        "type": "object",
        "properties": {
            "reportType": {
                "type": "string",
                "description": "The category or type of health locker files to retrieve."
            }
        },
        "required": ["reportType"]
    }
}

view_specific_record_declaration = {
    "name": "view_specific_record",
    "description": "Views a specific file from the currently logged-in member's health locker.",
    "parameters": {
        "type": "object",
        "properties": {
            "reportType": {
                "type": "string",
                "description": "The category of the health record to be viewed."
            },
            "fileId": {
                "type": "integer",
                "description": "The exact ID of the file to view."
            }
        },
        "required": ["reportType", "fileId"]
    }
}

remove_specific_record_declaration = {
    "name": "remove_specific_record",
    "description": "Permanently deletes a specific file from the currently logged-in member's health locker.",
    "parameters": {
        "type": "object",
        "properties": {
            "reportType": {
                "type": "string",
                "description": "The category of the health record from which the file will be removed."
            },
            "fileId": {
                "type": "integer",
                "description": "The exact ID of the file to be deleted."
            }
        },
        "required": ["reportType", "fileId"]
    }
}

fetch_all_members_scheduled_calls_under_cn_declaration = {
    "name": "get_all_care_navigator_scheduled_calls",
    "description": "Retrieves all upcoming scheduled calls for all members under a care navigator within a specified date range.",
    "parameters": {
        "type": "object",
        "properties": {
            "startDate": {
                "type": "string",
                "description": "The start date for the search in 'YYYY-MM-DD' format."
            },
                "endDate": {
                    "type": "string",
                    "description": "The end date for the search in 'YYYY-MM-DD' format."
            }
        },
        "required": ["startDate", "endDate"]
    }
}

fetch_todays_tasks_declaration = {
    "name": "get_todays_tasks",
    "description": "Retrieves a list of all tasks that are scheduled to be completed on the current day.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

fetch_weekly_summary_declaration = {
    "name": "get_weekly_summary",
    "description": "Retrieves a summary (count) of all calls and services scheduled for a specific week.",
    "parameters": {
        "type": "object",
        "properties": {
            "startDate": {
                "type": "string",
                "description": "The start date of the week in YYYY-MM-DD format."
            }
        },
        "required": ["startDate"]
    }
}

fetch_members_stratification_declaration = {
    "name": "get_all_members_stratification",
    "description": "Retrieves the risk stratification for all members under a care navigator based on a specific health condition.",
    "parameters": {
        "type": "object",
        "properties": {
            "conditionName": {
                "type": "string",
                "description": "The name of the health condition to use for stratifying the members."
            }
        },
        "required": ["conditionName"]
    }
}

fetch_pathway_breakup_declaration = {
    "name": "get_all_members_pathway_breakup",
    "description": "Retrieves a categorized summary of all members progress on a health pathway under a care navigator, based on a specific health condition.",
    "parameters": {
        "type": "object",
        "properties": {
            "conditionName": {
                "type": "string",
                "description": "The name of the health condition for which to fetch the pathway breakup."
            }
        },
        "required": ["conditionName"]
    }
}

fetch_new_report_members_declaration = {
    "name": "get_new_report_members",
    "description": "Retrieves a list of members under the care navigator who have new reports within a specified date range.",
    "parameters": {
        "type": "object",
        "properties": {
            "startDate": {
                "type": "string",
                "description": "The start date for the search in 'YYYY-MM-DD' format."
            },
            "endDate": {
                "type": "string",
                "description": "The end date for the search in 'YYYY-MM-DD' format."
            }
        },
        "required": ["startDate", "endDate"]
    }
}

fetch_requested_services_declaration = {
    "name": "get_requested_services",
    "description": "Retrieves a list of requested services within a specified date range, with optional filtering by service type and status.",
    "parameters": {
        "type": "object",
        "properties": {
            "startDate": {
                "type": "string",
                "description": "The start date for the search in 'YYYY-MM-DD' format."
            },
            "endDate": {
                "type": "string",
                "description": "The end date for the search in 'YYYY-MM-DD' format."
            },
            "requestType": {
                "type": "string",
                "description": "An optional filter for the type of service requested. Defaults to 'All'.",
                "enum": ["All", "Medication Requests", "Lab Requests", "Home Care Requests", "Home Based Vaccines", "Telehealth Services"]
            },
            "requestStatus": {
                "type": "string",
                "description": "An optional filter for the status of the service request. Defaults to 'all'.",
                "enum": ["all", "delayed", "inprogress", "completed"]
            }
        },
        "required": ["startDate", "endDate"]
    }
}

fetch_working_plans_and_breaks_declaration = {
    "name": "get_working_plans_and_breaks",
    "description": "Retrieves the current care navigator's work schedule, including working hours and break times.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

add_break_declaration = {
    "name": "add_break",
    "description": "Schedules a new break for a care navigator.",
    "parameters": {
        "type": "object",
        "properties": {
            "stratDateTime": {
                "type": "string",
                "description": "The start date and time of the break in 'YYYY-MM-DD HH:mm:ss' format (e.g. `2025-04-12 00:00:00`)"
            },
            "endDateTime": {
                "type": "string",
                "description": "The end date and time of the break in 'YYYY-MM-DD HH:mm:ss' format. (e.g. `2025-04-12 15:30:00`)"
            },
            "reason": {
                "type": "string",
                "description": "The reason for the break."
            }
        },
        "required": ["stratDateTime", "endDateTime", "reason"]
    }
}

delete_break_declaration = {
    "name": "delete_break",
    "description": "Deletes a previously scheduled break for a care navigator within a specific time range.",
    "parameters": {
        "type": "object",
        "properties": {
            "startDateTime": {
                "type": "string",
                "description": "The start date and time of the break in 'DD-MM-YYYY HH:mm am/pm' format."
            },
            "endDateTime": {
                "type": "string",
                "description": "The end date and time of the break in 'DD-MM-YYYY HH:mm am/pm' format."
            }
        },
        "required": ["startDateTime", "endDateTime"]
    }
}

search_view_member_under_cn_declaration = {
    "name": "search_view_member_under_cn",
    "description": "Searches for and retrieves a list of members and their data under the care navigator. The search is based on an optional search string, which can be a full or partial member name. If no search string is provided, all members will be returned.",
    "parameters": {
        "type": "object",
        "properties": {
            "searchStr": {
                "type": "string",
                "description": "An optional search string to filter members by name. This can be a full or partial name. Defaults to an empty string to return all members."
            }
        }
    }
}

fetch_calender_calls_declaration = {
    "name": "get_calender_calls",
    "description": "Fetch all scheduled, completed or cancelled calls for all members under the care navigator. This tool does not use a specific date range and returns all available calls.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

add_bmi_declaration = {
    "name": "add_bmi",
    "description": "Calculates and records the Body Mass Index (BMI) for the currently logged-in member.",
    "parameters": {
        "type": "object",
        "properties": {
            "height": {
                "type": "number",
                "description": "The member's height in centimeters (cm)."
            },
            "weight": {
                "type": "number",
                "description": "The member's weight in kilograms (kg)."
            },
            "metricDate": {
                "type": "string",
                "description": "The date when the height and weight were measured, in 'YYYY-MM-DD' format."
            }
        },
        "required": ["height", "weight","metricDate"]
    }
}

fetch_member_call_history_declaration = {
    "name": "member_call_history",
    "description": "Fetch call history of currently logged-in member under the navigator.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

# {
    # "startDate": "2025-08-28",
    # "endDate": "2025-09-03",
    # "searchStr": "",
    # "searchTaskType": "",
    # "searchPriority": "",
    # "searchStatus": "overdue,new,risk",
    # "searchCarenavigator": "OWh0NSsrOXpEZU5POXEyL21Td2tMZz09",
    # "searchPrograms": "",
    # "searchConditions": "",
    # "searchCompletedBy": "",
    # "searchContract": "",
    # "calledFrom": "tasklist",
    # "page": 1,
    # "perPage": 10,
    # "sortColumn": "",
    # "sortDirection": "asc",
    # "download": "N"
# } 

fetch_task_list_declaration = {
    "name": "get_task_list",
    "description": "Fetches a list of tasks for the currently logged-in care navigator. The tasks can be filtered by date range, type, priority, status, program, and condition.",
    "parameters": {
        "type": "object",
        "properties": {
            "startDate": {
                "type": "string",
                "description": "The start date to fetch tasks, in 'YYYY-MM-DD' format."
            },
            "endDate": {
                "type": "string",
                "description": "The end date to fetch tasks, in 'YYYY-MM-DD' format."
            },
            "taskType": {
                "type": "array",
                "description": "An array of strings to filter tasks by their type. For example: ['CareNavigator Call', 'WhatsApp Reply'].",
                "items": {
                    "type": "string",
                    # "enum": ["cncall", "labApproval", "labrequest", "medicationrequest", "memberreachout", "reportinterpretation", "servicesfailed", "telehealthconsultation", "whatsappreply"]
                }
            },
            "priority": {
                "type": "array",
                "description": "An array of strings to filter tasks by priority. For example: ['high', 'medium'].",
                "items": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low"]
                }
            },
            "searchStatus": {
                "type": "array",
                "description": "An optional array of strings to filter tasks by status. For example: ['risk', 'expired'].",
                "items": {
                    "type": "string",
                    "enum": ["overdue", "risk", "new", "completed", "dismissed", "expired"]
                }
            },
            "searchPrograms":{
                "type": "array",
                "description": "An optional array of strings to filter tasks by program. For example: ['ACM Pro', 'lifestyle changes'].",
                "items": {
                    "type": "string",
                    "enum": ["ACM Pro", "Aramco Preventive", "Cardiac Program", "Care Connect Model", "Care Connect Model For COPD", "lifestyle changes", "Light CCM", "Men Health", "WomenHealth", "World Class Global Expertise"]
                }
            },
            "searchConditions": {
                "type": "array",
                "description": "An optional array of strings to filter tasks by condition. For example: ['Dyslipidemia', 'Rheumatoid Arthritis'].",
                "items": {
                    "type": "string",
                    "enum": ["Arrhythmia", "Asthma", "Case Coordination", "COPD", "Diabetes Mellitus", "Diabetes with hypothyroidism", "Diabetic Kidney Disease", "Dyslipidemia", "Healthy Body", "Hypertension", "Hyperthyroidism", "Hypothyroidism", "Laboratory Management", "Medication Management", "Mental Health", "Mental Health Club two", "Physical Health Club One", "Rheumatoid Arthritis", "Systemic Lupus Erythematosus", "Well Controlled", "XXXYY"]
                }
            }
        },
        "required": ["startDate", "endDate", "taskType", "priority"]
    }
} 


TOOLS = [
    types.Tool(
        function_declarations=[add_note_declaration, disenroll_member_declaration, add_health_metric_declaration, fetch_services_by_category_declaration, add_new_service_declaration,
                               raise_new_ticket_declaration, fetch_program_details_declaration, assign_program_declaration, fetch_user_assigned_programs_declaration, 
                               stop_condition_declaration, restart_condition_declaration, remove_condition_declaration, fetch_available_pathways_for_program_condition_declaration,
                               change_pathway_declaration, fetch_member_upcoming_scheduled_call_declaration, cancel_or_reschedule_call_declaration, fetch_available_tickets_declaration,
                               add_comment_on_ticket_declaration, fetch_lab_providers_declaration, lab_request_declaration, fetch_homecare_lab_providers_declaration, 
                               fetch_homecare_health_products_declaration, homebase_vaccine_request_declaration, fetch_scheduled_calls_under_cn_declaration, fetch_userinfo_by_name_query_declaration,
                               schedule_call_with_cn_declaration, fetch_member_profile_details_declaration, fetch_user_health_metric_data_declaration, fetch_member_notes_history_declaration,
                               fetch_member_journey_declaration, add_member_record_declaration, fetch_health_locker_files_declaration, view_specific_record_declaration,
                               remove_specific_record_declaration, fetch_all_members_scheduled_calls_under_cn_declaration, fetch_todays_tasks_declaration,
                               fetch_weekly_summary_declaration, fetch_members_stratification_declaration, fetch_pathway_breakup_declaration, fetch_new_report_members_declaration,
                               fetch_requested_services_declaration, fetch_working_plans_and_breaks_declaration, add_break_declaration, delete_break_declaration,
                               search_view_member_under_cn_declaration, fetch_calender_calls_declaration, add_bmi_declaration, fetch_member_call_history_declaration,
                               fetch_task_list_declaration]
    )
]
