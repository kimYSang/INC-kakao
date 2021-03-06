from selenium import webdriver
import json
import pandas,time
import requests
import upload_file
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome('C:/chromedriver')

# 웹 자원 로드를 위해 3초 대기
driver.implicitly_wait(3)

# 평생교육원 채팅방 url 호출
driver.get('https://center-pf.kakao.com/_EvRij/chats')

# 로그인하기
# 아이디/패스워드 입력하기
driver.find_element_by_id('loginEmail').send_keys('skuinc.internship@skuniv.ac.kr') #아이디 보안상 삭제함
driver.find_element_by_id('loginPw').send_keys('!@#$intern12') #비번은 보안상 삭제함

# 로그인 버튼 클릭하기
driver.find_element_by_xpath('//*[@id="login-form"]/fieldset/button').click()

num = 1;
chat_list = driver.find_element_by_xpath('//*[@id="mArticle"]/div[2]/div[3]/div/div').find_elements_by_tag_name('li')
main_window = driver.window_handles[0] # 부모창

chat_items = []
nickName = '';

for i in chat_list:
    i.click()

# 모든 채팅방 열기
for i in chat_list:
    # 닉네임 가져오기
    print(i.find_element_by_class_name('txt_name').text)
    nickName = i.find_element_by_class_name('txt_name').text

    # 창 변환
    driver.switch_to_window(driver.window_handles[num])

    # 맨위로 스크롤하기 if문 + body선택
    #element = driver.find_element_by_class_name('bg_line')
    #element.click()
    #element.send_keys(Keys.PAGE_UP)

    scroll_count = 10
    while scroll_count > 0:  # 50번 반복
        #driver.find_element_by_class_name('popup_body').click()
        #driver.find_element_by_class_name('popup_body').send_keys(Keys.HOME)
        time.sleep(1)
#        element.send_keys(Keys.HOME)
        element = driver.find_element_by_tag_name('body')
        element.click()
        element.send_keys(Keys.HOME)
        scroll_count -= 1

    # 채팅방에서 item_chat 가져오기
    chats = driver.find_elements_by_class_name('item_chat')
    print(driver.current_url)

    # 유저 url 가져와서 chatlogs url로 변환
    idUrl = str(driver.current_url).split('/').pop()
    print(idUrl)
    url = 'https://center-pf.kakao.com/api/profiles/_EvRij/chats/' + idUrl + '/chatlogs'
    print(url)
    driver.get(url)

    # chatlogs text -> json 변환
    myJson = json.loads(driver.find_element_by_tag_name('body').text)

    # chatlogs json -> data로 변환
    for item in myJson['items']:
        #full_time = time.strftime("%D %H:%M", time.localtime(int(item['send_at'])) / 1000)
        #item_time = full_time.split(' ')
        result_ms = pandas.to_datetime(str(int(item['send_at'])/1000), unit='s')
        full_time = str(result_ms).split(' ')

        chat_item = {}

        chat_item['date'] = full_time[0]
        chat_item['time'] = full_time[1]
        chat_item['name'] = nickName
        chat_item['message'] = item['message']
        '''
        if(len(item['attachment']) > 1):
            img = item['attachment']['url']
            #urllib.urlretrieve(img, img)
            chat_item['img'] = img
        '''
        try:
            img_url = item['attachment']['url']
            filename = img_url.split('/')[-1]
            r = requests.get(img_url, allow_redirects=True)
            open(filename, 'wb').write(r.content)
            chat_item['img'] = img_url
            upload_file.saveImage(filename)
        except Exception :
            pass

        print(json.dumps(chat_item, ensure_ascii=False, indent="\t"))
#    for chat in chats:
#        if 'set_chat/a' in chat.find_element_by_class_name('*'):
#            print(chat.find_element_by_tag_name('set_chat/a').get_attribute('href'))
#        img = chat.find_element_by_class_name('link_pic').get_attribute('href')
#        if img != None:
#            print(img)

#        try :
#            print(chat.find_element_by_class_name('link_pic').get_attribute('href'))
#        except Exception :
#              pass

#        print(chat.text)
#        print('-----------------------------------')
    num += 1
    driver.switch_to_window(main_window)
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.NUMPAD1)

# 카톡방 열기
# 특정 카톡방 클릭 -> 모든 카톡방 열기
#driver.find_element_by_xpath('//*[@id="mArticle"]/div[2]/div[3]/div/div/li[3]').click()

chatting_window = driver.window_handles[1] # 자식창