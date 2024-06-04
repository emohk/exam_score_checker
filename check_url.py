from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import re
import key_manager

# correct and wrong symbols
CORRECT_ICON_PATH = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Eo_circle_green_white_checkmark.svg/1024px-Eo_circle_green_white_checkmark.svg.png?20200417133735'
WRONG_ICON_PATH = 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Red_X.svg/800px-Red_X.svg.png'

# Returns a tuple of result
def check_from_url(url):
    # Opening HTML file from given url
    try:
        response = requests.get(url)
        html_content = response.content
    except requests.RequestException:
        print('Url can\'t be opened')
        return
    soup = BeautifulSoup(html_content, 'html.parser')

    #total number f questions
    total, correct, incorrect = 0, 0, 0

    # Checking if response sheet contains option IDS (if yes, answer key is stored in a db)
    if re.search(r'Option \w ID :\d+', soup.get_text()):
        key = get_db(soup)
        #defining pattern of MCQ responses
        mcqPtrn = re.compile(r'Q\.(.+)Options(?:.+\. )+Question Type :MCQQuestion ID :(\d+)(?:Option \w ID :\d+)+Status :(?:Not )?AnsweredChosen Option :(.)')
        #defining pattern of subjective questions
        saPtrn = re.compile(r'Q\.(.+)Given Answer :(\w+)Question Type :(\w+)Question ID :(\d+)Status :(?:Not )?.*')

        #checking each question
        for div in soup.find_all('div', class_="question-pnl"):
            total += 1 #increment number of questions

            text = div.get_text() # all text in a question

            # checking answered status and skips if not answered
            status = re.findall(r'Status :(.*(?:Not )?.*)', text)[0]
            if 'Not' in status:
                continue

            #checking if question is Mcq
            if mcqPtrn.search(text):
                match = mcqPtrn.findall(text)[0]
                optionID = re.findall(fr'Option {match[2]} ID :(\d+)', text)[0]
                if key_manager.is_right_ans(match[1], optionID, 'jee_05_04_2024_evening'):
                    correct += 1
                    add_symbol('correct', div, soup)
                else:
                    incorrect += 1
                    add_symbol('wrong', div, soup)

            #checking if question is subjective
            elif saPtrn.search(text):
                match = saPtrn.findall(text)[0]
                if key_manager.is_right_ans(match[3], match[1], key):
                    correct += 1
                    add_symbol('correct', div, soup)
                else:
                    incorrect += 1
                    add_symbol('wrong', div, soup)

        # for ensuring all images load properly
        add_domain_to_img(soup, 'https://cdn.digialm.com//')

        return (correct, incorrect, total - correct - incorrect, soup.prettify())
    # if answer key not in a db there may be tick/wrong symbol next to options
    else:
        # defining pattern of info
        ptrn = re.compile(r'Q\.(\d+)Ans(?:\d.*)*Question Type :\w+Question ID :\d+Status :((?:Not )?.*)Chosen Option :(.+)')

        for div in soup.find_all('div', class_="question-pnl"):
            total += 1

            text = div.get_text()

            match = ptrn.findall(text)[0]
            # skips question if not answered
            if 'Not' in match[1]:
                continue

            if correctAns := div.find_all('td', class_='rightAns'):
                for a in range(len(correctAns)):
                    correctAns[a] =  correctAns[a].get_text(strip=True)[0]
            else:
                correctAns = 'BONUS'

            # if user answered correct or if it is a bonus question
            if match[2] in correctAns or correctAns == 'BONUS':
                correct += 1
                add_symbol('correct', div, soup)
            else:
                incorrect += 1
                add_symbol('wrong', div, soup)

        add_domain_to_img(soup, 'https://cdn.digialm.com//')
        return (correct, incorrect, total - correct - incorrect, soup.prettify())

# adds symbol of tick/wrong
def add_symbol(symbol, div, soup):
    menu = div.find('table', class_='menu-tbl')
    if not menu:
        print('Menu not found')
        return
    tr, td = soup.new_tag('tr'), soup.new_tag('td')
    if symbol == 'correct':
        img = soup.new_tag('img', src=CORRECT_ICON_PATH, alt='correct', style='height: 80px')
    elif symbol == 'wrong':
        img = soup.new_tag('img', src=WRONG_ICON_PATH, alt='wrong', style='height: 80px')
    else:
        print('Invalid symbol')
        return
    
    td.append(img)
    tr.append(td)
    menu.append(tr)

# for ensuring all images load properly
def add_domain_to_img(soup, domain):
    img_tags = soup.find_all('img')
    
    for img_tag in img_tags:
        src = img_tag.get('src')
        if src:
            if img_tag['src'] == CORRECT_ICON_PATH or img_tag['src'] == WRONG_ICON_PATH:
                continue
            parsed_src = urlparse(src)
            if not parsed_src.netloc:
                # If domain name is not present in src, prepend it
                img_tag['src'] = urljoin(domain, src)
                
    return str(soup)

# gets the name of key(table in db)
def get_db(soup):
    infobox = soup.find('div', class_="main-info-pnl").get_text()
    infos = re.findall(r'Test Date.*(\d{2}/\d{2}/\d{4}).*Test Time(?: |:)*(\d{1,2}):', infobox)[0]
    date = re.sub('/', '_', infos[0])
    shift = 'morning' if 7 <= int(infos[1]) <= 10 else 'evening'
    return 'jee' + '_' + date + '_' + shift
