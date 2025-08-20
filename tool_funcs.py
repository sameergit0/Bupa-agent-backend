from enc_dec import make_request
from datetime import datetime, date, timedelta
from dateutil.tz import gettz
import webbrowser
from constants import DynamicConstants

def add_note(dynamic_constants: DynamicConstants, notes: str):
    """Add notes for the member"""

    endpoint_name = "/add_notes"
    data = {"userId": dynamic_constants.user_id, "notes": notes}

    try: 
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output
    except Exception as e:
        return {"error": str(e)}
    
def disenroll_member(dynamic_constants: DynamicConstants, reason: str, disEnrollmentNote: str):
    """De-enroll member from the program"""

    endpoint_name = "/request_disenrollment"
    disEnrollmentReason = dynamic_constants.reason_lookup.get(reason)
    data = {"userId": dynamic_constants.user_id, "disEnrollmentReason": disEnrollmentReason, "disEnrollmentNote": disEnrollmentNote}

    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output
    except Exception as e:
        return {"error": str(e)}

def add_health_metric(dynamic_constants: DynamicConstants, metricsName: str, metricsVal: int, metricsDate: str):
    """Log health metric for the member"""

    endpoint_name = "/add_generic_metrics_vals"
    membershipNo = dynamic_constants.user_profile["data"]["info"]["membershipNumber"]
    metrics_lookup = {entry["metricsName"]: entry for entry in dynamic_constants.metrics_details_list}
    details = metrics_lookup.get(metricsName)
    if details is None:
        raise ValueError(f"Unknown metricName: {metricsName!r}")
    metricsId = details["metricsId"]
    keyword   = details["keyword"]
    data = {"formData": {"userId": dynamic_constants.user_id, "membershipNo": membershipNo,"metricsName": metricsName, "metricsVal": metricsVal, "metricsDate": metricsDate, "metricsId": metricsId, "keyword": keyword}}
    print(data)
    
    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output
    except Exception as e:
        return {"error": str(e)}

def services_by_category(dynamic_constants: DynamicConstants, categoryName: str):
    """Fetches all the services under any category"""

    endpoint_name = "/fetch_service_by_category"
    categoryId = dynamic_constants.category_lookup.get(categoryName)
    if categoryId is None:
        raise ValueError(f"Unknown category name: {categoryName!r}")
    data = {"categoryId": categoryId}

    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def add_new_service(dynamic_constants: DynamicConstants, categoryName: str, serviceName: str, date: str, time: str, notes: str = ""):
    """Add new service for member"""

    endpoint_name = "/add_member_additional_services"
    services_resp = services_by_category(dynamic_constants, categoryName)
    services_list = services_resp.get("services", [])
    if not services_list:
        raise ValueError(f"No services found under category: {categoryName!r}")
    service_lookup = {s["serviceName"]: s["serviceId"] for s in services_list}
    serviceId = service_lookup.get(serviceName)
    if serviceId is None:
        raise ValueError(f"Unknown service name: {serviceName!r}. " 
                         f"Choose from: {list(service_lookup)}")
    pathways = dynamic_constants.user_profile["data"]["info"]["memberPathways"]
    if not pathways:
        raise RuntimeError("No active pathway found for member")
    pathwayId = pathways[0]["pathwayId"]
    data = {"userId": dynamic_constants.user_id, "formData": {"pathwayId": pathwayId, "categoryId": dynamic_constants.category_lookup[categoryName], "serviceId": serviceId, "date": date, "time": time, "notes": notes}}
    
    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output
    except Exception as e:
        return {"error": str(e)}

def raise_new_ticket(dynamic_constants: DynamicConstants, title: str, ticketType: str, priority: str, description: str):
    """Raise or Add new ticket for the member"""

    endpoint_name = "/add_new_ticket"
    membershipNo = dynamic_constants.user_profile["data"]["info"]["membershipNumber"]
    type = dynamic_constants.ticket_type_lookup.get(ticketType)
    data = {"membershipNo": membershipNo, "type": type, "title": title, "priority": priority, "description": description, "files": "[]"}

    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output
    except Exception as e:
        return {"error": str(e)}

def program_details(dynamic_constants: DynamicConstants):
    """Fetches available programs, their conditions and that conditions pathways"""

    endpoint_name = "/fetch_program_condition_pathway"
    data = {"userId": dynamic_constants.user_id}

    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def assign_program(dynamic_constants: DynamicConstants, programName: str, conditionName: str, pathwayName: str = ""):
    """Assign new program to the member"""

    endpoint_name = "/add_new_program"
    programs_info = program_details(dynamic_constants)

    programs_list = programs_info["programs"]
    selected_program = next((p for p in programs_list if p["programName"] == programName),None)
    if not selected_program:
        available_programs = [p["programName"] for p in programs_list]
        return {"error": f"Unknown program name: '{programName}'. Available programs: {available_programs}"}  
    programId = selected_program["programId"]

    conditions = selected_program.get("conditions", [])
    selected_condition = next((c for c in conditions if c["conditionName"] == conditionName),None)
    if not selected_condition:
        available_conditions = [c["conditionName"] for c in conditions]
        return {"error": f"Unknown condition name: '{conditionName}' under program '{programName}'. Available conditions: {available_conditions}"}
        
    conditionId = selected_condition["conditionId"]

    pathwayId = ""
    if pathwayName:
        pathways = selected_condition.get("pathways", [])
        selected_pathway = next((pw for pw in pathways if pw["pathwayName"] == pathwayName),None)
        if not selected_pathway:
            available_pathways = [pw["pathwayName"] for pw in pathways]
            return {"error": f"Unknown pathway name: '{pathwayName}' under condition '{conditionName}'. Available pathways: {available_pathways}"}
        pathwayId = selected_pathway["pathwayId"]

    data = {"userId": dynamic_constants.user_id, "formData": {"programId": programId, "conditionId": conditionId, "pathwayId": pathwayId}}

    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output
    except Exception as e:
        return {"error": str(e)}

def user_assigned_programs(dynamic_constants: DynamicConstants):
    """Fetches a list of all programs currently assigned to the member"""
    
    member_profile = dynamic_constants.fetch_user_profile_details()

    try:
        return member_profile.get("data", {}).get("info", {})
    except Exception as e:
        return {"error": str(e)}

def stop_condition(dynamic_constants: DynamicConstants, pathwayName: str, remarks: str):
    """Stop an active condition of member"""

    endpoint_name = "/stop_pathway"
    member_info = user_assigned_programs(dynamic_constants)
    member_pathways = member_info.get("memberPathways", [])
    selected_pathway = next((p for p in member_pathways if p["pathwayName"] == pathwayName),None)
    if not selected_pathway:
        available_active_pathways = [p["pathwayName"] for p in member_pathways if p.get("pathwayStatus") == "active"]
        return {"error": f"The pathway '{pathwayName}' could not be found or is not a active pathway. "
                        f"Available active pathways: {available_active_pathways}"}
    if selected_pathway.get("pathwayStatus") != "active":
        return {"error": f"The pathway '{pathwayName}' cannot be stopped as its status is '{selected_pathway.get('pathwayStatus')}', not 'active'."}
    pathwayId = selected_pathway.get("pathwayId")
    pathwayRelId = selected_pathway.get("pathwayRelId")
    data = {"userId":dynamic_constants.user_id, "pathwayId": pathwayId, "pathwayRelId": pathwayRelId, "remarks": remarks}

    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output
    except Exception as e:
        return {"error": str(e)}
    
def restart_condition(dynamic_constants: DynamicConstants, pathwayName: str, remarks: str):
    """Restarts a previously stopped condition for a member."""

    endpoint_name = "/restart_pathway"
    member_info = user_assigned_programs(dynamic_constants)
    member_pathways = member_info.get("memberPathways", [])
    selected_pathway = next((p for p in member_pathways if p["pathwayName"] == pathwayName),None)
    if not selected_pathway:
        available_stopped_pathways = [p["pathwayName"] for p in member_pathways if p.get("pathwayStatus") == "stopped"]
        return {"error": f"The pathway '{pathwayName}' could not be found or is not a stopped pathway. "
                        f"Available stopped pathways: {available_stopped_pathways}"}
    if selected_pathway.get("pathwayStatus") != "stopped":
        return {"error": f"The pathway '{pathwayName}' cannot be restarted as its status is '{selected_pathway.get('pathwayStatus')}', not 'stopped'."}
    pathwayId = selected_pathway.get("pathwayId")
    pathwayRelId = selected_pathway.get("pathwayRelId")
    data = {"userId":dynamic_constants.user_id, "pathwayId": pathwayId, "pathwayRelId": pathwayRelId, "remarks": remarks}

    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output
    except Exception as e:
        return {"error": str(e)}

def remove_condition(dynamic_constants: DynamicConstants, conditionName: str):
    """Remove pathway condition of member"""

    endpoint_name = "/remove_pathway"
    member_info = user_assigned_programs(dynamic_constants)
    member_pathways = member_info.get("memberPathways", [])
    selected_condition = next((p for p in member_pathways if p["conditionName"] == conditionName),None)
    if not selected_condition:
        return {"error": f"The condition '{conditionName}' could not be found for the member."}

    if selected_condition.get("pathwayStatus") != "notset":
        return {"error": f"The condition '{conditionName}' cannot be removed because its pathway status is "
                         f"'{selected_condition.get('pathwayStatus')}', not 'notset'."}
    
    pathwayRelId = selected_condition.get("pathwayRelId")

    data = {"userId":dynamic_constants.user_id, "pathwayRelId": pathwayRelId}

    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output
    except Exception as e:
        return {"error": str(e)}

def available_pathways_for_program_condition(dynamic_constants: DynamicConstants, programName: str, conditionName: str):
    """Fetches all available pathways for a specific program and condition from a member's assigned programs"""

    endpoint_name = "/fetch_pathways"
    member_info = user_assigned_programs(dynamic_constants)
    member_pathways = member_info.get("memberPathways", [])
    assigned_program_condition = next((p for p in member_pathways if p["programName"] == programName and p["conditionName"] == conditionName),None)
    if not assigned_program_condition:
        return {"error": f"Program '{programName}' with condition '{conditionName}' not found in member's assigned programs."}
    
    programId = assigned_program_condition.get("programId")
    conditionId = assigned_program_condition.get("conditionId")
    oldPathwayId = assigned_program_condition.get("pathwayId")

    data = {"userId": dynamic_constants.user_id, "programId": programId, "conditionId": conditionId, "oldPathwayId": oldPathwayId}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def change_pathway(dynamic_constants: DynamicConstants, programName: str, conditionName: str, oldPathwayName: str, newPathwayName: str, notes: str = ""):
    """Change members pathway for a specific condition in the program"""

    endpoint_name = "/assign_pathway"
    member_info = user_assigned_programs(dynamic_constants)
    member_pathways = member_info.get("memberPathways", [])
    assigned_program_condition = next((p for p in member_pathways if p["programName"] == programName and p["conditionName"] == conditionName and p["pathwayName"] == oldPathwayName), None)
    if not assigned_program_condition:
        return {"error": f"Could not find an assigned pathway matching '{oldPathwayName}' under program '{programName}' and condition '{conditionName}'."}
    programId = assigned_program_condition.get("programId")
    conditionId = assigned_program_condition.get("conditionId")
    oldPathwayId = assigned_program_condition.get("pathwayId")

    new_pathway_details = available_pathways_for_program_condition(dynamic_constants, programName, conditionName)
    pathways_list = new_pathway_details.get("pathways", [])
    if not pathways_list:
        return {"error": f"No pathways available for program '{programName}' and condition '{conditionName}'."}
    new_pathway_match = next((p for p in pathways_list if p["pathwayName"] == newPathwayName),None)
    if not new_pathway_match:
        available_pathway_names = [p["pathwayName"] for p in pathways_list]
        return {"error": f"New pathway '{newPathwayName}' not found. Available pathways are: {available_pathway_names}"}
    newPathwayId = new_pathway_match.get("pathwayId")
    
    data = {"userId": dynamic_constants.user_id, "programId": programId, "conditionId": conditionId, "oldPathwayId": oldPathwayId, "pathwayId": newPathwayId, "notes": notes}

    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output 
    except Exception as e:
        return {"error": str(e)}

def member_scheduled_calls(dynamic_constants: DynamicConstants):
    """Fetches appointmnet details of the member"""

    endpoint_name = "/fetch_user_specific_calls"
    data = {"userId": dynamic_constants.user_id}
    try:
        response = make_request(endpoint_name=endpoint_name, data=data)
        if response and response.get("code") == 200 and "calls" in response.get("data", {}):
            all_calls = response["data"]["calls"]
            scheduled_calls = [call for call in all_calls if call.get("nonScheduled") == "N"]
            output = {"code": 200, "data": {"calls": scheduled_calls}}
            return output.get("data", {})
        else:
            return {"error": "No calls scheduled for member."}
    except Exception as e:
        return {"error": str(e)}
    
def cancel_or_reschedule_call(dynamic_constants: DynamicConstants, action: str, old_slot_date: str, old_slot_time: str, new_slot: str = "", streamName: str = "", reasonForCancellation: str = ""):
    """Cancel or re-schedule call for the member"""

    endpoint_name = "/cancel_or_reschedule_appointment"
    scheduled_calls_data = member_scheduled_calls(dynamic_constants)
    all_scheduled_calls = scheduled_calls_data["calls"]
    target_appointment = next((call for call in all_scheduled_calls if call.get("date") == old_slot_date and call.get("time") == old_slot_time), None)
    if not target_appointment:
            return {"error": f"No scheduled appointment found for the specified slot {old_slot_date} {old_slot_time}"}
    appointmentId = target_appointment.get("callId")
    streamValue = dynamic_constants.streams_lookup.get(streamName)
    streams = [{"label": streamName,"value": streamValue}]

    data = {"userId": dynamic_constants.user_id, "action": action, "appointmentId": appointmentId, "slot": new_slot if action == "re-schedule" else "", "streams": streams if action == "cancel" else [],
            "reasonForCancellation": reasonForCancellation if action == "cancel" else ""}
    
    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
    except Exception as e:
        return {"error": str(e)}

def available_tickets(dynamic_constants: DynamicConstants):
    """Fetches member's available tickets"""

    endpoint_name = "/list_all_tickets"
    membershipNo = dynamic_constants.user_profile["data"]["info"]["membershipNumber"]
    data = {"perPage": 7, "pageNumber": 1, "membershipNo": membershipNo}

    try:
        output = make_request(endpoint_name=endpoint_name, data=data)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}
    
def add_comment_on_ticket(dynamic_constants: DynamicConstants, ticketTitle: str, comment: str):
    """Add comment on raised ticket"""

    endpoint_name = "/comment_on_ticket"
    members_all_tickets_info = available_tickets(dynamic_constants)
    all_tickets = members_all_tickets_info.get("tickets", [])
    selected_ticket = next((p for p in all_tickets if p.get("title") == ticketTitle),None)
    if not selected_ticket:
        available_titles = [t["title"] for t in all_tickets]
        return {"error": f"Ticket with title '{ticketTitle}' not found. Available titles: {available_titles}"}
    encTicketId = selected_ticket.get("encTicketId")

    data = {"comment": comment, "ticketId": encTicketId, "commentBy": "carenavigator"}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
    except Exception as e:
        return {"error": str(e)}

def lab_providers(dynamic_constants: DynamicConstants, cityName: str):
    """Fetches all the lab providers in a given city"""

    endpoint_name = "/fetch_form_data"

    data = {"cityId": dynamic_constants.city_lookup.get(cityName), "membership": dynamic_constants.user_profile["data"]["info"]["membershipNumber"]}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}
    
def lab_request(dynamic_constants: DynamicConstants, coPayment: str, preferredAppointmentDateTime: str, cityName: str, partnerClinic: str, requestedLabTest: str, labProviderName: str,
                deductible: str = "NIL", nationality: str = "Saudi Arabian", district: str = "", remarks: str = "", approvalNumber: int = ""):
    """Make Lab request for the member"""

    endpoint_name = "/save_lab_request_metadoc"

    available_lab_providers = lab_providers(dynamic_constants, cityName=cityName)
    lab_providers_list = available_lab_providers.get("lab", [])
    if not lab_providers_list:
        raise ValueError(f"No lab providers available in : {cityName!r}")
    lab_provider_lookup = {l["labName"]: l["id"] for l in lab_providers_list}
    labProviderId = lab_provider_lookup.get(labProviderName)

    data = {
        "formData": {
            "userId": dynamic_constants.user_id,
            "membership": dynamic_constants.user_profile["data"]["info"]["membershipNumber"],
            "name": dynamic_constants.user_profile["data"]["info"]["memberName"],
            "mobileNumber": dynamic_constants.user_profile["data"]["info"]["mobile"],
            "imageUrl": dynamic_constants.user_profile["data"]["info"]["imageUrl"],
            "coPayment": coPayment,
            "deductible": deductible if coPayment == 'yes' else "NIL",
            "selectedDate": preferredAppointmentDateTime,
            "viewDate": datetime.strptime(preferredAppointmentDateTime, "%Y-%m-%d %H:%M").replace(tzinfo=gettz("Asia/Kolkata")).astimezone(gettz("UTC")).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "nationality": nationality,
            "labProviderName": labProviderName,
            "labProviderId": labProviderId,
            "district": district,
            "remarks": remarks,
            "approvalNumber": approvalNumber if isinstance(approvalNumber, int) else "",
            "city": cityName,
            "cityId": dynamic_constants.city_lookup.get(cityName),
            "partnerClinic": dynamic_constants.partner_lookup.get(partnerClinic),
            "requestedLabTest": dynamic_constants.labtest_lookup.get(requestedLabTest),
            "selectedUserNames": dynamic_constants.labtest_lookup.get(requestedLabTest),
            "productCount": "1"
        }
    }
    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
    except Exception as e:
        return {"error": str(e)}

def homecare_lab_providers(dynamic_constants: DynamicConstants, cityName: str):
    """Fetches all the home care lab providers available in a given city"""

    endpoint_name = "/fetch_home_care"

    data = {"cityName": dynamic_constants.city_lookup.get(cityName), "membership": dynamic_constants.user_profile["data"]["info"]["membershipNumber"]}
    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def homecare_health_products(dynamic_constants: DynamicConstants, cityName: str, categoryName: str):
    """Fetches all the home care health product for a given category available in a given city"""

    endpoint_name = "/fetch_home_care"

    data = {"cityName": dynamic_constants.city_lookup.get(cityName), "categoryName": dynamic_constants.hc_cat_lookup.get(categoryName), "membership": dynamic_constants.user_profile["data"]["info"]["membershipNumber"]}
    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def home_care_request(dynamic_constants: DynamicConstants, coPayment: str, preferredAppointmentDateTime: str, cityName: str, categoryName: str, labProviderName: str, productName: str,
                      nationality: str = "Saudi Arabian", deductible: str = "NIL", district: str = "", remarks: str = "", approvalNumber: int = ""):
    """make home care request for the member"""

    endpoint_name = "/save_home_care_metadoc"

    available_hc_lab_providers = homecare_lab_providers(dynamic_constants, cityName=cityName)
    hc_lab_providers_list = available_hc_lab_providers.get("provider", [])
    if not hc_lab_providers_list:
        raise ValueError(f"No home care lab providers available in : {cityName!r}")
    hc_lab_provider_lookup = {hc["providerName"]: hc["id"] for hc in hc_lab_providers_list}
    homeHealthCareId = hc_lab_provider_lookup.get(labProviderName)
    
    available_hc_products = homecare_health_products(dynamic_constants, cityName=cityName, categoryName=categoryName)
    hc_products_list = available_hc_products.get("products", [])
    if not hc_products_list:
        raise ValueError(f"No home care products available for category {categoryName} in {cityName!r}")
    hc_products_lookup = {hc["label"]: hc["value"] for hc in hc_products_list}
    product = hc_products_lookup.get(productName)

    data = {
        "formData": {
            "userId": dynamic_constants.user_id,
            "membership": dynamic_constants.user_profile["data"]["info"]["membershipNumber"],
            "name": dynamic_constants.user_profile["data"]["info"]["memberName"],
            "mobileNumber": dynamic_constants.user_profile["data"]["info"]["mobile"],
            "approvalNumber": approvalNumber if isinstance(approvalNumber, int) else "",
            "coPayment": coPayment,
            "deductible": deductible if coPayment == 'yes' else "NIL",
            "selectedDate": preferredAppointmentDateTime,
            "viewDate": datetime.strptime(preferredAppointmentDateTime, "%Y-%m-%d %H:%M").replace(tzinfo=gettz("Asia/Kolkata")).astimezone(gettz("UTC")).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "nationality": nationality,
            "district": district or "",
            "remarks": remarks or "",
            "city": cityName,
            "cityId": dynamic_constants.city_lookup.get(cityName),
            "partnerClinic": "Direct Request",
            "category": categoryName,
            "labProviderName": labProviderName,
            "homeHealthCare": homeHealthCareId,
            "product": product
        }
    }

    output = make_request(data=data, endpoint_name=endpoint_name)
    return output

def homebase_vaccine_request(dynamic_constants: DynamicConstants, cityName: str, productName: str, deductible: str, vaccine: str, district: str, nationality: str = "Saudi Arabian", remarks: str = ""):
    """Adds home base vaccine request for the member"""

    endpoint_name = "/save_home_base_metadoc"

    data = {
    "formData": {
        "userId": dynamic_constants.user_id,
        "membership": dynamic_constants.user_profile["data"]["info"]["membershipNumber"],
        "name": dynamic_constants.user_profile["data"]["info"]["memberName"],
        "mobileNumber":dynamic_constants.user_profile["data"]["info"]["mobile"],
        "city": cityName,
        "cityId": dynamic_constants.city_lookup.get(cityName),
        "partnerClinic": "Direct Request",
        "deductible": deductible,
        "vaccine": vaccine,
        "nationality": nationality,
        "district": district,
        "remarks": remarks or "",
        "requestedHomeHealth": dynamic_constants.hb_product_lookup.get(productName),
        }
    }

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
    except Exception as e:
        return {"error": str(e)}   

def scheduled_calls_under_cn(dynamic_constants: DynamicConstants):
    """Fetch all scheduled calls for members assigned to care navigator."""

    endpoint_name = "/fetch_calender_calls"

    data = {}

    try:
        response = make_request(data=data, endpoint_name=endpoint_name)
        if response and response.get("code") == 200 and "calls" in response.get("data", {}):
            all_calls = response["data"]["calls"]
            scheduled_calls = [call for call in all_calls if call.get("status") == "Scheduled"]
            output = {"code": 200, "data": {"calls": scheduled_calls}}
            return output.get("data", {})
        else:
            return {"error": "No calls scheduled under care navigator."}
    except Exception as e:
        return {"error": str(e)}

def userinfo_by_name_query(dynamic_constants: DynamicConstants, searchQuery: str):
    """Fetches user info by name for scheduling calls"""

    endpoint_name = "/fetch_users_list_v2"

    data = {"searchStr": searchQuery, "appliedFilter": {}, "pageNumber": 1}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def schedule_call_with_cn(dynamic_constants: DynamicConstants, memberName: str, appointmentDateTime):
    """Schedule member's call with care navigator"""

    endpoint_name = "/schedule_carenavigator_call"
    users_info = userinfo_by_name_query(dynamic_constants, searchQuery=memberName)
    user_names_list = users_info.get("users", [])
    if not user_names_list:
        return {"error": f"No members found matching the search query: '{memberName}'."}
    member_lookup = {user["memberName"]: user["userId"] for user in user_names_list}
    userId = member_lookup.get(memberName)

    data = {"userId": userId,"date": appointmentDateTime}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
    except Exception as e:
        return {"error": str(e)}

def member_profile_details(dynamic_constants: DynamicConstants):
    """Retrieve all available information about a member"""

    endpoint_name = "/fetch_user_profile_v2"

    data = {"userId": dynamic_constants.user_id}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def user_health_metric_data(dynamic_constants: DynamicConstants, metricName: str):
    """Fetch a member's logged health data for a specific metric."""

    endpoint_name = "/fetch_vital_graph"
    metrics_lookup = {entry["metricsName"]: entry for entry in dynamic_constants.metrics_details_list}
    details = metrics_lookup.get(metricName)
    if details is None:
        raise ValueError(f"Unknown metricName: {metricName!r}")
    metricsId = details["metricsId"]

    data = {"userId": dynamic_constants.user_id, "metricsId": metricsId}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def member_notes_history(dynamic_constants: DynamicConstants):
    """Retrieve all added notes history for a member"""

    endpoint_name = "/fetch_notes_list"

    data = {"userId": dynamic_constants.user_id}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def member_journey(dynamic_constants: DynamicConstants):
    """Retrieves full 360° member's journey"""

    endpoint_name = "/fetch_member_360profile"

    data = {"membershipNumber": dynamic_constants.user_profile["data"]["info"]["membershipNumber"]}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def add_member_record(dynamic_constants: DynamicConstants, reportType: str, description: str):
    """Add a new record for a member"""

    endpoint_name = "/add_healthlocker_file"

    file = dynamic_constants.select_file()
    if file.get("error"):
        return {"error": file["error"]}
    file_data = file.get("fileData")
    file_name = file.get("originalFileName")
    data = {"userId": dynamic_constants.user_id, "formData": {"reportTypeId": dynamic_constants.report_type_lookup.get(reportType), "title": description, "file": file_data,"originalName": file_name}}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
    except Exception as e:
        return {"error": str(e)}

def health_locker_files(dynamic_constants: DynamicConstants, reportType: str):
    """retrieves a list of files that a user has uploaded for a particular report type"""

    endpoint_name = "/fetch_healthlocker_files_v2"

    data = {"userId": dynamic_constants.user_id, "reportTypeId": dynamic_constants.report_type_lookup.get(reportType)}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def view_specific_record(dynamic_constants: DynamicConstants, reportType: str, fileName: str):
    """view a specific file from a user's health locker"""

    endpoint_name = "/fetch_healthlocker_file_url"

    try:
        file_list_data = health_locker_files(dynamic_constants, reportType)
        file_id = None
        files = file_list_data.get("files", [])
        for file_info in files:
            if file_info.get("originalFileName") == fileName:
                file_id = file_info.get("fileId")
                break
        if file_id is None:
            return {"error": f"File '{fileName}' not found under report type '{reportType}'."}
        
        data = {"fileId": file_id}
        response = make_request(data=data, endpoint_name=endpoint_name)
        file_url = response.get("data", {}).get("fileUrl")
        return {"File": webbrowser.open_new_tab(file_url)}
    except Exception as e:
        return {"error": str(e)}

def remove_specific_record(dynamic_constants: DynamicConstants, reportType: str, fileName: str):
    """"Remove a specific record from member's health locker"""

    endpoint_name = "/remove_healthlocker_files"

    try:
        file_list_data = health_locker_files(dynamic_constants, reportType)
        file_id = None
        files = file_list_data.get("files", [])
        for file_info in files:
            if file_info.get("originalFileName") == fileName:
                file_id = file_info.get("fileId")
                break
        if file_id is None:
            return {"error": f"File '{fileName}' not found under report type '{reportType}'."}
        
        data = {"fileId": file_id}

        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
        
    except Exception as e:
        return {"error": str(e)}

def get_all_care_navigator_scheduled_calls(dynamic_constants: DynamicConstants, startDate: str, endDate: str):
    """Retrives all scheduled members calls under the care navigator"""

    endpoint_name = "/fetch_upcoming_appointments_list"

    data = {"startDate": startDate, "endDate": endDate, "pageNumber": 1}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def get_todays_tasks(dynamic_constants: DynamicConstants):
    """Fetches list of all tasks to be completed today"""

    endpoint_name = "/fetch_other_tasks_list"

    data = {}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}    

def get_weekly_summary(dynamic_constants: DynamicConstants, startDate: str):
    """Fetches weekly summary of calls and services"""

    endpoint_name = "/fetch_weekly_summary"

    try:
        yesterday = date.today() - timedelta(days=1)
        start_date_obj = datetime.strptime(startDate, "%Y-%m-%d").date()
        total_days = (start_date_obj - yesterday).days
        weekCount = total_days // 7
        
        data = {"weekCount": weekCount}

        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}  

def get_all_members_stratification(dynamic_constants: DynamicConstants, conditionName: str):
    """Retrieves all member's stratification for a specific condition under the care navigator"""

    endpoint_name = "/diabetic_data"

    data = {"extraParams": {"conditionId": dynamic_constants.condition_lookup.get(conditionName)}}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def get_all_members_pathway_breakup(dynamic_constants: DynamicConstants, conditionName: str):
    """Retrieves all member's pathway breakup for a specific condition under the care navigator"""

    endpoint_name = "/pathway_breakup_v2"

    data = {"conditionId": dynamic_constants.condition_lookup.get(conditionName)}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def get_new_report_members(dynamic_constants: DynamicConstants, startDate: str, endDate: str):
    """Fetches list of member's with new reports"""

    endpoint_name = "/fetch_new_reports"

    data = {"requestStartDate": startDate, "requestEndDate": endDate, "pageNumber": 1}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def get_requested_services(dynamic_constants: DynamicConstants, startDate: str, endDate: str, requestType: str = "all", requestStatus: str = "all"):
    """Retrieves all the requested services """

    endpoint_name = "/fetch_home_based_service_tracking_v2"

    request_type_code = dynamic_constants.request_type_lookup.get(requestType)

    data = {"requestType": request_type_code, "requestStartDate": startDate, "requestEndDate": endDate, "requestStatus": requestStatus}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def get_working_plans_and_breaks(dynamic_constants: DynamicConstants):
    """Retrives working plans and breaks of care navigator"""

    endpoint_name = "/fetch_working_plans_and_breaks"

    data = {}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def add_break(dynamic_constants: DynamicConstants, stratDateTime: str, endDateTime: str, reason: str):
    """Adds appointment break for care navigator"""

    endpoint_name = "/save_appointment_break"

    data = {"start": stratDateTime, "end": endDateTime, "reason": reason}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
    except Exception as e:
        return {"error": str(e)}

def delete_break(dynamic_constants: DynamicConstants, startDateTime: str, endDateTime: str):
    """Removes previously scheduled break for a care navigator"""

    endpoint_name = "/remove_appointment_break"

    plan_breaks = get_working_plans_and_breaks(dynamic_constants)
    all_breaks = plan_breaks.get("breaks", [])
    selected_break = next((b for b in all_breaks if b.get("start") == startDateTime and b.get("end") == endDateTime), None)

    if not selected_break:
        return {"error": f"No break found from '{startDateTime}' to {endDateTime} for carenavigator"}
    breakId = selected_break.get("id")

    data = {"breakId": breakId}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
    except Exception as e:
        return {"error": str(e)}

def search_view_member_under_cn(dynamic_constants: DynamicConstants, searchStr: str = ""):
    """"Searches and views member under the care navigator"""

    endpoint_name = "/fetch_users_list_v2"

    data = { "searchStr": searchStr, "appliedFilter": {}, "pageNumber": 1, "messageStatus": "all"}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
    except Exception as e:
        return {"error": str(e)}

def get_calender_calls(dynamic_constants: DynamicConstants):
    """"Retrieves all the scheduled, cancelled or completed calls for all mambers under a care navigator"""

    endpoint_name = "/fetch_calendar_calls"

    data = {}

    try:
        output = make_request(data=data, endpoint_name=endpoint_name)
        return output
    except Exception as e:
        return {"error": str(e)}    

TOOL_MAP = {
    "add_note": add_note,
    "disenroll_member": disenroll_member,
    "add_health_metric": add_health_metric,
    "services_by_category": services_by_category,
    "add_new_service": add_new_service,
    "raise_new_ticket": raise_new_ticket,
    "program_details": program_details,
    "assign_program": assign_program,
    "user_assigned_programs": user_assigned_programs,
    "stop_condition": stop_condition,
    "restart_condition": restart_condition,
    "remove_condition": remove_condition,
    "available_pathways_for_program_condition": available_pathways_for_program_condition,
    "change_pathway": change_pathway,
    "member_scheduled_calls": member_scheduled_calls,
    "cancel_or_reschedule_call": cancel_or_reschedule_call,
    "available_tickets": available_tickets,
    "add_comment_on_ticket": add_comment_on_ticket,
    "lab_providers": lab_providers,
    "lab_request": lab_request,
    "homecare_lab_providers": homecare_lab_providers,
    "homecare_health_products": homecare_health_products,
    "home_care_request": home_care_request,
    "homebase_vaccine_request": homebase_vaccine_request,
    "scheduled_calls_under_cn": scheduled_calls_under_cn,
    "userinfo_by_name_query": userinfo_by_name_query,
    "schedule_call_with_cn": schedule_call_with_cn,
    "member_profile_details": member_profile_details,
    "user_health_metric_data": user_health_metric_data,
    "member_notes_history": member_notes_history,
    "member_journey": member_journey,
    "add_member_record": add_member_record,
    "health_locker_files": health_locker_files,
    "view_specific_record": view_specific_record,
    "remove_specific_record": remove_specific_record,
    "get_all_care_navigator_scheduled_calls": get_all_care_navigator_scheduled_calls,
    "get_todays_tasks": get_todays_tasks,
    "get_weekly_summary": get_weekly_summary,
    "get_all_members_stratification": get_all_members_stratification,
    "get_all_members_pathway_breakup": get_all_members_pathway_breakup,
    "get_new_report_members": get_new_report_members,
    "get_requested_services": get_requested_services,
    "get_working_plans_and_breaks": get_working_plans_and_breaks,
    "add_break": add_break,
    "delete_break": delete_break,
    "search_view_member_under_cn": search_view_member_under_cn,
    "get_calender_calls": get_calender_calls
}
