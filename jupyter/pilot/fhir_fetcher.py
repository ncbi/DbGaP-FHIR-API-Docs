import requests
import json

def fetch_all_data(session, url, num_pages=0, print_entry='n'):
    all_entries = []
    page_counter = 0  # Initialize page counter

    while url:
        try:
            response = session.get(url)  # Use session to make the GET request
            response.raise_for_status()
            data = response.json()
            entries = data.get('entry', [])
            all_entries.extend(entries)

            # Increment the page counter after successfully fetching a page
            page_counter += 1

            # Pretty-print the JSON data returned in this iteration
            if print_entry == 'y':
                print("Data returned in this iteration:")
                for entry in entries:
                    print(json.dumps(entry, indent=4))

            next_link = None
            for link in data.get('link', []):
                if link.get('relation') == 'next':
                    next_link = link.get('url')
                    break

            # If num_pages is 0, keep fetching until there are no more pages.
            # If num_pages is not 0, check if the desired number of pages has been reached.
            if num_pages != 0 and page_counter >= num_pages:
                break

            url = next_link
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # HTTP error
            try:
                error_content = response.json()
                print(f"Response content: {json.dumps(error_content, indent=4)}")  # Pretty-print JSON response
            except ValueError:
                print(f"Response content: {response.content}")  # Response content for debugging
            break
        except Exception as err:
            print(f"Other error occurred: {err}")  # Other errors
            break
    return all_entries
