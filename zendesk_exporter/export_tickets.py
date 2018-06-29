import json
import requests
import urllib
import argparse
import time

domain_name = None
email = None
api_key = None

def search_tickets(start, end):
    encoded_query = urllib.urlencode({"query": "type:ticket created>%s created<%s" % (start, end)})
    url = "https://%s.zendesk.com/api/v2/search.json?%s" % (domain_name, encoded_query)
    all_results = []
    while url is not None:
        response = requests.get(url, auth=(email + "/token", api_key))
        all_results += response.json()['results']
        print "Fetched %d/%d ticket id\'s" % (len(all_results), response.json()['count'])
        url = response.json().get('next_page', None)
    return all_results

def fetch_ticket_ids(start, end):
    search_result = search_tickets(start, end) 
    return [x["id"] for x in search_result]

def fetch_tickets(ticket_ids):
    tickets = []
    for i, ticket_id in enumerate(ticket_ids):
        
        response = requests.get("https://%s.zendesk.com/api/v2/tickets/%s.json?include=comment_count,users" % (domain_name, ticket_id),
                        auth=(email + "/token", api_key))
        users = response.json().get("users", [])
        end_user = [x for x in users if x["role"] == "end-user"]
        not_end_users = [x for x in users if x["role"] != "end-user"]
        ticket = response.json()["ticket"]
        if len(end_user) > 0:
            ticket["end_user_name"] = end_user[0]["name"]
        else:
            ticket["end_user_name"] = ""
        ticket["support_names"] = ",".join([n["name"] for n in not_end_users])
        tickets.append(ticket)
        print "Fetched %d/%d tickets" % (i+1, len(ticket_ids))
    return tickets

def fetch_comments(ticket_ids):
    all_comments = []
    for i, ticket_id in enumerate(ticket_ids):
        url = "https://%s.zendesk.com/api/v2/tickets/%s/comments.json?include=users" % (domain_name, ticket_id)
        new_comments = []
        while url is not None:
            response = requests.get(url, auth=(email + "/token", api_key))
            users = response.json()["users"]
            new_comments += response.json()["comments"]
            url = response.json().get('next_page', None)
        
        for comment in new_comments:
            comment["ticket_id"] = ticket_id
            comment["name"] = [x for x in users if x["id"] == comment["author_id"]][0]["name"]
            all_comments.append(comment)
        print "Fetched %d/%d ticket comments" % (i+1, len(ticket_ids))
    return all_comments

ticket_field_names = "id,created_at,subject,description,tags,updated_at,end_user_name,support_names".split(",")
comment_field_names = "ticket_id,body,created_at,public,name".split(",")

def export_to_csv(tickets, comments, file_name, quick=False):
    _ext = '.csv'
    file_name = file_name + _ext if not file_name.endswith(_ext) else file_name

    print "\nExporting to CSV"

    import csv
    with open(file_name, 'wb') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        if quick:
            writer.writerow(tickets[0].keys())
            for ticket in tickets:
                row = []
                for k in ticket:
                    if k not in ticket:
                        row.append("")
                    elif type(ticket[k]) in (unicode, int, str):
                        row.append(ticket[k])
                    else:
                        row.append(str(ticket[k]))
                writer.writerow([v.encode('utf-8') if type(v) is unicode else v for v in row])
        else:
            writer.writerow(ticket_field_names)
            for ticket in tickets:
                row = []
                for k in ticket_field_names:
                    if k not in ticket:
                        row.append("")
                    elif type(ticket[k]) in (unicode, int, str):
                        row.append(ticket[k])
                    else:
                        row.append(str(ticket[k]))
                writer.writerow([v.encode('utf-8') if type(v) is unicode else v for v in row])


def export_to_excel(tickets, comments, file_name):
    from openpyxl import Workbook
    _ext = '.xlsx'
    file_name = file_name + _ext if not file_name.endswith(_ext) else file_name

    print "\nExporting to Excel file: %s" % file_name
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active
    ws.title = "tickets"

    # Rows can also be appended
    ws.append(ticket_field_names)
    for ticket in tickets:
        row = []
        for k in ticket_field_names:
            if k not in ticket:
                row.append("")
            elif type(ticket[k]) in (unicode, int, str):
                row.append(ticket[k])
            else:
                row.append(str(ticket[k]))
        ws.append(row)

    if comments:  
        ws2 = wb.create_sheet(title="Comments")
        ws2.append(comment_field_names)
        for comment in comments:
            row = []
            for k in comment_field_names:
                if k not in comment:
                    row.append("")
                elif type(comment[k]) in (unicode, int, str):
                    row.append(comment[k])
                else:
                    row.append(str(comment[k]))
            ws2.append(row)

    # Save the file
    wb.save("%s" % file_name)
    print "Done"

example_json_file = """
{
    "domain_name": "XXX",
    "email": "XXX",
    "api_key": "XXX",
    "start_date": "2018-06-27",
    "end_date": "2018-06-30",
    "fetch_comments": false,
    "output_file_name": "last_6_months",
    "output_file_type": "csv"
}
"""

def main():
    global domain_name
    global email
    global api_key

    parser = argparse.ArgumentParser()
    parser.add_argument("job_file", help="path to the json job file")
    args = parser.parse_args()

    with open(args.job_file) as f:
        job = json.load(f)

    required_params = {"domain_name", "email", "api_key"}
    missing_params = required_params - set(job.keys())
    if missing_params:
        raise RuntimeError("Missing required parameters: %s. Sample json file:\n%s" % (missing_params, example_json_file))
    
    domain_name = job["domain_name"]
    email = job["email"]
    api_key = job["api_key"]

    start_date = job.get("start_date")
    end_date = job.get("end_date")
    file_name = job.get("output_file_name", str(int(time.time())))
    

    # ticket_ids = fetch_ticket_ids(start_date, end_date)
    # tickets = fetch_tickets(ticket_ids)
    comments = [] # fetch_comments(ticket_ids) if job.get("fetch_comments") else []
    if job.get("output_file_type", "").lower() == "csv":
        export_to_csv(search_tickets(start_date, end_date), comments, file_name, quick=True)
    else:
        export_to_excel(tickets, comments, file_name)

if __name__ == "__main__":
    main()