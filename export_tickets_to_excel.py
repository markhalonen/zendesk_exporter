import json
import requests
from openpyxl import Workbook
import urllib
import argparse
import time
from secrets import *

def fetch_ticket_ids(start, end):
    encoded_query = urllib.urlencode({"query": "type:ticket created>%s created<%s" % (start, end)})
    url = "https://%s.zendesk.com/api/v2/search.json?%s" % (domain_name, encoded_query)
    all_results = []
    while url is not None:
        response = requests.get(url, auth=(email + "/token", api_key))
        all_results += response.json()['results']
        print 'Fetched %d/%d ticket id\'s' % (len(all_results), response.json()['count'])
        url = response.json().get('next_page', None)
    return [x["id"] for x in all_results]

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
    for i, ticket_id in enumerate(ticket_ids):
        url = "https://%s.zendesk.com/api/v2/tickets/%s/comments.json?include=users" % (domain_name, ticket_id)
        all_comments = []
        while url is not None:
            response = requests.get(url, auth=(email + "/token", api_key))
            users = response.json()["users"]
            all_comments += response.json()["comments"]
            url = response.json().get('next_page', None)
        
        for comment in all_comments:
            comment["ticket_id"] = ticket_id
            comment["name"] = [x for x in users if x["id"] == comment["author_id"]][0]["name"]
            comments.append(comment)
        print "Fetched %d/%d ticket comments" % (i+1, len(ticket_ids))

def export_to_csv(tickets, comments, file_name):
    raise NotImplementedError("CSV not implemented")

def export_to_excel(tickets, comments, file_name):
    ticket_field_names = "id,created_at,subject,description,tags,updated_at,end_user_name,support_names".split(",")
    comment_field_names = "ticket_id,body,created_at,public,name".split(",")

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", help="Start date YYYY-MM-DD", required=True)
    parser.add_argument("--end", help="End date YYYY-MM-DD", required=True)
    parser.add_argument("--skip-comments", help="Don't fetch the comments. This will speed it up", action="store_true")
    parser.add_argument("--excel-file-name", help="The name for the excel file.")
    args = parser.parse_args()

    start_date = args.start
    end_date = args.end
    skip_comments = args.skip_comments
    excel_file_name = args.excel_file_name
    _ext = '.xlsx'
    excel_file_name = excel_file_name + _ext if not excel_file_name.endswith(_ext) else excel_file_name

    ticket_ids = fetch_ticket_ids(start_date, end_date)
    tickets = fetch_tickets(ticket_ids)
    comments = [] if skip_comments else fetch_comments(ticket_ids)
    export_to_excel(tickets, comments, excel_file_name or str(int(time.time())))

if __name__ == "__main__":
    main()