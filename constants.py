from enc_dec import make_request
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
import base64
import os
import mimetypes
import concurrent.futures

class DynamicConstants:
    def __init__(self, user_id, access_token, cn_id=None):
        self.user_id = user_id if user_id is not None else ""
        self.access_token = access_token
        self.cn_id = cn_id
        self.user_profile = None
        self.disenrollment_reasons_list = []
        self.reason_names = []
        self.reason_lookup = {}
        self.metrics_details_list = []
        self.metric_name_unit_list = []
        self.servies_categories_list = []
        self.service_category_names = []
        self.category_lookup = {}
        self.ticket_types_list = []
        self.ticket_type_category_names = []
        self.ticket_type_lookup = {}
        self.streams_list = []
        self.stream_names = []
        self.streams_lookup = {}
        self.city_names = []
        self.city_lookup = {}
        self.partner_names = []
        self.partner_lookup = {}
        self.labtest_names = []
        self.labtest_lookup = {}
        self.hc_cat_names = []
        self.hc_cat_lookup = {}
        self.hb_product_names = []
        self.hb_product_lookup = {}
        self.report_type_names = []
        self.report_type_lookup = {}
        self.condition_names = []
        self.condition_lookup = {}
        self.request_type_lookup = {
            "All": "all",
            "Medication Requests": "mr",
            "Lab Requests": "lr",
            "Home Care Requests": "hcr",
            "Home Based Vaccines": "hbv",
            "Telehealth Services": "ths"
        }
        self.break_reason_names = []
        self.task_type_names = []
        self.task_type_lookup = {}
        self.task_list = {}

    def load(self):
        self.user_profile = self.fetch_user_profile_details()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_fetch = {
                executor.submit(self.fetch_disenrollment_reasons): "disenrollment_reasons",
                executor.submit(self.fetch_health_metric_details): "health_metric_details",
                executor.submit(self.fetch_service_categories): "service_categories",
                executor.submit(self.fetch_ticket_types): "ticket_types",
                executor.submit(self.fetch_call_cancellation_streams): "streams",
                executor.submit(self.fetch_form_data_details): "form_data_details",
                executor.submit(self.fetch_home_care_details): "home_care_details",
                executor.submit(self.fetch_home_base_details): "home_base_details",
                executor.submit(self.fetch_report_types): "report_types",
                executor.submit(self.fetch_conditions): "conditions",
                executor.submit(self.fetch_break_reasons): "break_reasons",
                executor.submit(self.fetch_task_types): "task_types"
            }

            results = {}
            for future in concurrent.futures.as_completed(future_to_fetch):
                fetch_name = future_to_fetch[future]
                try:
                    data = future.result()
                    results[fetch_name] = data
                except Exception as exc:
                    print(f'{fetch_name} generated an exception: {exc}')

        disenrollment_reasons = results.get("disenrollment_reasons", {})
        self.disenrollment_reasons_list = [{"reason": r["reason"], "recordId": r["recordId"]} for r in disenrollment_reasons.get("data", {}).get("reasons", [])]
        self.reason_names = [reason["reason"] for reason in self.disenrollment_reasons_list]
        self.reason_lookup = {reason["reason"]: reason["recordId"] for reason in self.disenrollment_reasons_list}

        health_metric_details = results.get("health_metric_details", {})
        self.metrics_details_list = [{"metricsName": m["metricsName"], "metricsId": m["metricsId"], "keyword": m["keyword"], "unit": m["unit"]} for m in health_metric_details.get("data", {}).get("metrics", [])]
        self.metric_name_unit_list = [{"metricsName": entry["metricsName"], "unit": entry["unit"]} for entry in self.metrics_details_list]

        service_categories = results.get("service_categories", {})
        self.servies_categories_list = [{"categoryName": c["categoryName"], "categoryId": c["categoryId"]} for c in service_categories.get("data", {}).get("categories", [])]
        self.service_category_names = [category["categoryName"] for category in self.servies_categories_list]
        self.category_lookup = {entry["categoryName"]: entry["categoryId"] for entry in self.servies_categories_list}

        ticket_types = results.get("ticket_types", {})
        self.ticket_types_list = [{"ticket_type": t["ticket_type"], "id": t["id"]} for t in ticket_types.get("data", {}).get("ticketTypes", [])]
        self.ticket_type_category_names = [ticket["ticket_type"] for ticket in self.ticket_types_list]
        self.ticket_type_lookup = {entry["ticket_type"]: entry["id"] for entry in self.ticket_types_list}

        streams = results.get("streams", {})
        self.streams_list = [{"streamName": c["label"], "streamId": c["value"]} for c in streams.get("data", {}).get("status", {}).get("Cancelled", [])]
        self.stream_names = [stream["streamName"] for stream in self.streams_list]
        self.streams_lookup = {stream["streamName"]: stream["streamId"] for stream in self.streams_list}

        form_data_details = results.get("form_data_details", {})
        self.city_names = [item.get('label') for item in form_data_details.get('data', {}).get('city', []) if item.get('label')]
        self.city_lookup = {item.get('label'): item.get('value') for item in form_data_details.get('data', {}).get('city', []) if item.get('label') and item.get('value')}
        self.partner_names = [item.get('partnerName') for item in form_data_details.get('data', {}).get('partner', []) if item.get('partnerName')]
        self.partner_lookup = {item.get('partnerName'): item.get('id') for item in form_data_details.get('data', {}).get('partner', []) if item.get('partnerName') and item.get('id')}
        self.labtest_names = [item.get('label') for item in form_data_details.get('data', {}).get('labTest', []) if item.get('label')]
        self.labtest_lookup = {item.get('label'): item.get('value') for item in form_data_details.get('data', {}).get('labTest', []) if item.get('label') and item.get('value')}

        home_care_details = results.get("home_care_details", {})
        self.hc_cat_names = [item.get('label') for item in home_care_details.get('data', {}).get('category', []) if item.get('label')]
        self.hc_cat_lookup = {item.get('label'): item.get('categoryName') for item in home_care_details.get('data', {}).get('category', []) if item.get('label') and item.get('categoryName')}

        home_base_details = results.get("home_base_details", {})
        if home_base_details and home_base_details.get('data') and home_base_details.get('data').get('products'):
            self.hb_product_names = [item.get('label') for item in home_base_details.get('data', {}).get('products', []) if item.get('label')]
            self.hb_product_lookup = {item.get('label'): item.get('id') for item in home_base_details.get('data', {}).get('products', []) if item.get('label') and item.get('id')}
        else:
            self.hb_product_names = []
            self.hb_product_lookup = {}

        report_types = results.get("report_types", {})
        self.report_type_names = [item.get('reportType') for item in report_types.get('data', {}).get('reportTypes', []) if item.get('reportType')]
        self.report_type_lookup = {item.get('reportType'): item.get('reportTypeId') for item in report_types.get('data', {}).get('reportTypes', []) if item.get('reportType') and item.get('reportTypeId')}

        conditions = results.get("conditions", {})
        self.condition_names = [item.get('conditionName') for item in conditions.get('data', {}).get('conditions', []) if item.get('conditionName')]
        self.condition_lookup = {item.get('conditionName'): item.get('conditionId') for item in conditions.get('data', {}).get('conditions', []) if item.get('conditionName') and item.get('conditionId')}

        break_reasons = results.get("break_reasons", {})
        self.break_reason_names = [item.get('reason') for item in break_reasons.get('data', {}).get('reasons', []) if item.get('reason')]

        task_types = results.get("task_types", {})
        self.task_type_names = [item.get('taskDescription') for item in task_types.get('data', {}).get('taskTypes', []) if item.get('taskDescription')]
        self.task_type_lookup = {item.get('taskDescription'): item.get('taskType') for item in task_types.get('data', {}).get('taskTypes', []) if item.get('taskDescription') and item.get('taskType')}

        if self.user_profile and "data" in self.user_profile and "info" in self.user_profile["data"] and self.user_profile["data"]["info"]:
            self.task_list = self.cn_task_list()

    def select_file(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        messagebox.showinfo("Select File", "Please select file", parent=root)
        file_path = filedialog.askopenfilename(title="Select a file",filetypes=[("All files", "*.*")])
        root.destroy()

        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                base64_content = base64.b64encode(file_content).decode('utf-8')
                original_file_name = os.path.basename(file_path)
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                data_uri = f"data:{mime_type};base64,{base64_content}"
                file = {"fileData": data_uri, "originalFileName": original_file_name}
                return file
            except IOError as e:
                return {"error": f"Error reading file: {e}"}
        return {"error": "No file was selected"}

    def fetch_user_profile_details(self):
        """Fetches user profile details"""

        endpoint_name = "/fetch_user_profile_v2"
        data = {"userId": self.user_id}
        output = make_request(endpoint_name=endpoint_name, data=data, access_token=self.access_token)
        return output

    def fetch_disenrollment_reasons(self):
        """Fetches disenrollment reasons"""

        endpoint_name = "/fetch_disenrollment_reasons"
        if not (self.user_profile and "data" in self.user_profile and "info" in self.user_profile["data"] and self.user_profile["data"]["info"] and "memberPathways" in self.user_profile["data"]["info"] and self.user_profile["data"]["info"]["memberPathways"]):
            return {}
        mp = self.user_profile["data"]["info"]["memberPathways"][0]
        programId = mp.get("programId")
        conditionId = mp.get("conditionId")
        if not programId or not conditionId:
            return {}
        data = {"userId": self.user_id, "programId": programId, "conditionId": conditionId}
        output = make_request(endpoint_name=endpoint_name, data=data, access_token=self.access_token)
        return output

    def fetch_health_metric_details(self):
        """Feteches available metric names and their details like unit, keyword, etc."""

        endpoint_name = "/fetch_generic_health_metrics"
        data = {"userId": self.user_id}
        output = make_request(endpoint_name=endpoint_name, data=data, access_token=self.access_token)
        return output

    def fetch_service_categories(self):
        """Fetches all available service categories"""

        endpoint_name = "/fetch_service_categories"
        data = {}
        output = make_request(endpoint_name=endpoint_name, data=data, access_token=self.access_token)
        return output

    def fetch_ticket_types(self):
        """Fetches ticket types for raise ticket"""

        endpoint_name = "/fetch_all_ticket_types"
        data = {}
        output = make_request(endpoint_name=endpoint_name, data=data, access_token=self.access_token)
        return output

    def fetch_call_cancellation_streams(self):
        """Fetches streams for call cancellation"""

        endpoint_name = "/fetch_call_status"
        data = {}
        output = make_request(endpoint_name=endpoint_name, data=data, access_token=self.access_token)
        return output

    def fetch_form_data_details(self):
        """Fetchs required information for home based services"""

        endpoint_name = "/fetch_form_data"
        if not (self.user_profile and "data" in self.user_profile and "info" in self.user_profile["data"] and self.user_profile["data"]["info"] and "membershipNumber" in self.user_profile["data"]["info"]):
            return {}
        data = {"membership": self.user_profile["data"]["info"]["membershipNumber"]}
        output = make_request(data=data, endpoint_name=endpoint_name, access_token=self.access_token)
        return output

    def fetch_home_care_details(self):
        """Fetches required information for home care request"""

        endpoint_name = "/fetch_home_care"
        if not (self.user_profile and "data" in self.user_profile and "info" in self.user_profile["data"] and self.user_profile["data"]["info"] and "membershipNumber" in self.user_profile["data"]["info"]):
            return {}
        data = {"membership": self.user_profile["data"]["info"]["membershipNumber"]}
        output = make_request(data=data, endpoint_name=endpoint_name, access_token=self.access_token)
        return output

    def fetch_home_base_details(self):
        """Fetches required information for home base request"""

        endpoint_name = "/fetch_home_base"
        if not (self.user_profile and "data" in self.user_profile and "info" in self.user_profile["data"] and self.user_profile["data"]["info"] and "membershipNumber" in self.user_profile["data"]["info"]):
            return {}
        data = {"membership": self.user_profile["data"]["info"]["membershipNumber"]}
        output = make_request(data=data, endpoint_name=endpoint_name, access_token=self.access_token)
        return output

    def fetch_report_types(self):
        """fetches list of available record types"""

        endpoint_name = "/fetch_report_types"
        data = {}
        output = make_request(data=data, endpoint_name=endpoint_name, access_token=self.access_token)
        return output

    def fetch_conditions(self):
        """Fetches all the conditions for member stratification"""

        endpoint_name = "/fetch_conditions"
        data = {}
        output = make_request(data=data, endpoint_name=endpoint_name, access_token=self.access_token)
        return output

    def fetch_break_reasons(self):
        """Fetches break reason to add break"""

        endpoint_name = "/fetch_break_reasons"
        data = {}
        output = make_request(data=data, endpoint_name=endpoint_name, access_token=self.access_token)
        return output
    
    def fetch_task_types(self):
        """Fetches task types"""

        endpoint_name = "/fetch_task_types"
        data = {}
        output = make_request(data=data, endpoint_name=endpoint_name, access_token=self.access_token)
        return output
    
    def cn_task_list(self):
        """Fetches all tasks list for all member's under care navigator"""

        try:
            endpoint_name = "/fetch_task_list"
            today_date = datetime.now().date()
            start_date = today_date - timedelta(days=7)
            data = {"startDate": start_date.strftime("%Y-%m-%d"),
                    "endDate": today_date.strftime("%Y-%m-%d"),
                    "searchStr": self.user_profile["data"]["info"]["membershipNumber"],
                    "searchTaskType": "",
                    "searchPriority": "",
                    "searchStatus": "overdue,new,risk",
                    "searchCarenavigator": "OWh0NSsrOXpEZU5POXEyL21Td2tMZz09",
                    "searchPrograms": "",
                    "searchConditions": "",
                    "searchCompletedBy": "",
                    "searchContract": "",
                    "calledFrom": "tasklist",
                    "page": 1,
                    "perPage": 10,
                    "sortColumn": "",
                    "sortDirection": "asc",
                    "download": "N"} 
            print("data------------------------------------------------------------------------------------------------------------------", data)

            output = make_request(data=data, endpoint_name=endpoint_name, access_token=self.access_token)
            return output
        except Exception as e:
            return {"error": "Sorry, I can't fetch care navigator's task list at the moment. Please try again later."}
