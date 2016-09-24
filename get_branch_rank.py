import requests
from bs4 import BeautifulSoup

# For disabling the InsecurePlatForm warnings
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

import sys

BASE_URL = 'https://erp.iitkgp.ernet.in/StudentPerformance/view_performance.jsp?rollno='


def get_cg(url):
    cgpa = ''
    try:
        r = requests.Session()
        response = r.get(url)
        response.raise_for_status()
    except requests.Timeout:
        print('error: timed out for', url[len(BASE_URL):])
        return 0
    except requests.ConnectionError:
        print('error: connection problem for', url[len(BASE_URL):])
        return 0
    except requests.HTTPError:
        print('error: invalid HTTP response for', url[len(BASE_URL):])
        return 0
    except requests.exceptions.ChunkedEncodingError as e:
        print('error: ChunkedEncodingError', url)
        return 0
    soup = BeautifulSoup(response.text.replace('&nbsp', ''), 'lxml')
    tds = soup.find_all('td')
    for idx, td in enumerate(tds):
        if td.text.strip() == 'CGPA':
            cgpa = tds[idx + 1].text
            return cgpa


def get_rank(cg_list, mycg):
    sorted_list = []
    rank = 1
    for stud in cg_list:
        cg = stud.values()[0]
        # check for existent cg
        if bool(cg) and float(cg) > float(mycg):
            rank += 1
    return rank


def check_roll_and_return_cg(rollno):
    mycg = ''
    url = BASE_URL + rollno
    # print url
    try:
        r = requests.Session()
        response = r.get(url)
        response.raise_for_status()
    except requests.Timeout:
        print('error: timed out', url)
        return 0
    except requests.ConnectionError:
        print('error: connection problem', url)
        return 0
    except requests.HTTPError:
        print('error: invalid HTTP response', url)
        return 0
    except requests.exceptions.ChunkedEncodingError as e:
        print('error: ChunkedEncodingError', url)
        return 0

    soup = BeautifulSoup(response.text.replace('&nbsp', ''), 'lxml')
    tds = soup.find_all('td')
    for idx, td in enumerate(tds):
        if td.text.strip() == 'CGPA':
            mycg = tds[idx + 1].text
            return mycg

if __name__ == '__main__':
    rollno = raw_input('Enter your roll number please : ')
    rollno = rollno.replace(' ', '').upper()
    print 'Okay wait for some time...let me check'
    mycg = check_roll_and_return_cg(rollno)
    if not mycg or mycg == '':
        print """Hmm...it seems like there is some kind of an issue.\n
                Please try again."""
        sys.exit(0)
    cg_list = []
    # varialble to keep track of invalid roll numbers
    invalid_roll_count = 0
    # the final two digits of a roll number
    index = 1

    # if no roll number found for 5 times continuously I'll assume the branch's student list has ended
    while invalid_roll_count < 6:
        cg_json = {}

        # roll number genrated by the script
        dynamic_roll = rollno[:-2]
        if index < 10:
            dynamic_roll += '0' + str(index)
        else:
            dynamic_roll += str(index)
        # print dynamic_roll
        url = BASE_URL + dynamic_roll
        if dynamic_roll == rollno:
            pass
        # NOTE: check if it prints the user's url. It should not actually
        cgpa = get_cg(url)
        if not bool(cgpa):
            invalid_roll_count += 1
            print 'invalid_roll_count', invalid_roll_count
            index += 1
            continue
        # print url
        invalid_roll_count = 0
        index += 1
        cg_json[dynamic_roll] = cgpa
        cg_list.append(cg_json)
    # print cg_list
    print 'your cg', mycg
    final_rank = get_rank(cg_list, mycg)
    print 'your branch rank is', final_rank, 'out of ', (index - invalid_roll_count - 1), 'students in your branch'
