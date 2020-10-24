# -*- coding: utf-8 -*-
import re

import requests
from bs4 import BeautifulSoup

from .exceptions import AuthError, SessionError, ContentNotFound


def create_soup(html_page):
    return BeautifulSoup(html_page, 'lxml')


class ThreadReader:
    def __init__(self, thread, session=None, server=None):
        self.server = server or 'https://forum.antichat.ru'
        self.thread = thread
        self.http = session or requests.Session()

    def __parse_page(self, html):
        soup = create_soup(html)
        posts = []
        if not soup.find('ol', id='messageList'):
            error_message = (soup.find('div', class_='errorPanel') or
                             soup.find('div', class_='errorOverlay')).get_text().strip()
            raise ContentNotFound(error_message)
        for post_tag in soup.find('ol', id='messageList').findChildren('li', recursive=False):
            # Extract Antichat post ID (thread-independent)
            post_id = int(post_tag['id'].split('-')[-1])
            # Extract Antichat member ID
            try:
                poster_id = int(post_tag.find(
                    'div',
                    class_='messageUserInfo'
                ).find(
                    'div',
                    class_='uix_userTextInner'
                ).a['href'].split('/')[-2])
            except (ValueError, KeyError):
                poster_id = None
            # Extract poster nick
            poster_nick = post_tag['data-author']
            # Find message text tag
            content = post_tag.find(
                'blockquote',
                class_='messageText SelectQuoteContainer ugc baseHtml'
            )
            # Remove from it unnecessary quotes
            for s in content.find_all('div', class_='bbCodeBlock bbCodeQuote'):
                s.extract()
            # Replace smiles with their text alternative
            for s in content.find_all('img', class_=re.compile(r'mceSmilieSprite mceSmilie\d{1,2}')):
                s.replace_with(s['alt'])
            # Then extract text
            text = content.get_text().strip()
            posts.append({
                    'poster': {
                        'id': poster_id,
                        'nick': poster_nick
                    },
                    'id': post_id,
                    'text': text
                })
        return posts

    def read_page(self, page):
        html = self.http.get(f'{self.server}/threads/{self.thread}/page-{page}').text
        return self.__parse_page(html)

    def read(self, start_post=None, limit=None, offset=None):
        if limit is None:
            limit = float('inf')

        if start_post is not None:
            url = f'{self.server}/posts/{start_post}'
            r = self.http.get(url)
            if 'page' in r.url:
                match = re.search(
                    f'{self.server}/threads/{self.thread}/' + r'page-(\d+)',
                    r.url
                )
                if match:
                    page = int(match.group(1))
                else:
                    return False
            else:
                page = 1
            posts = self.__parse_page(r.text)
            start_index = 0
            for post in posts:
                if post['id'] == start_post:
                    break
                start_index += 1
            posts = posts[start_index:]
            page += 1
            while len(posts) < limit:
                r = self.http.get(f'{self.server}/threads/{self.thread}/page-{page}')
                curr_page = int(re.search(
                    f'{self.server}/threads/{self.thread}/' + r'page-(\d+)',
                    r.url).group(1)
                )
                # Check if we have reached the end
                if curr_page != page:
                    break
                posts += self.__parse_page(r.text)
                page += 1
        elif offset is not None:
            start_page = offset // 20 + 1
            url = f'{self.server}/threads/{self.thread}/page-{start_page}'
            r = self.http.get(url)
            if 'page' in r.url:
                page = int(
                    re.search(
                        f'{self.server}/threads/{self.thread}/' + r'page-(\d+)',
                        r.url
                    ).group(1)
                )
            else:
                page = 1
            posts = self.__parse_page(r.text)[(offset % 20):]
            if start_page == page:
                page += 1
                while len(posts) < limit:
                    r = self.http.get(f'{self.server}/threads/{self.thread}/page-{page}')
                    curr_page = int(
                        re.search(
                            f'{self.server}/threads/{self.thread}/' + r'page-(\d+)',
                            r.url
                        ).group(1))
                    # Check if we have reached the end
                    if curr_page != page:
                        break
                    posts += self.__parse_page(r.text)
                    page += 1
        else:
            page = 1
            posts = []
            while len(posts) < limit:
                r = self.http.get(f'{self.server}/threads/{self.thread}/page-{page}')
                curr_page = int(
                    re.search(
                        f'{self.server}/threads/{self.thread}/' + r'page-(\d+)',
                        r.url
                    ).group(1)
                )
                # Check if we have reached the end
                if curr_page != page:
                    break
                posts += self.__parse_page(r.text)
                page += 1

        if type(limit) == int:
            posts = posts[:limit]

        return posts


class Client:
    def __init__(self, username, password):
        self.server = 'https://forum.antichat.ru'
        session = requests.Session()
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
        AppleWebKit/537.36 (KHTML, like Gecko)\
        Chrome/81.0.4044.122 Safari/537.36'
        self.http = session
        self.username = username
        self.password = password

    def auth(self):
        self.http.post(
            f'{self.server}/login/login',
            data={
                'login': self.username,
                'password': self.password,
                'register': 0,
                'remember': 1,
            }
        )
        if self.http.cookies.get('anti_logged_in') != '1':
            raise AuthError('Invalid username or password')

    def logout(self):
        if self.http.cookies.get('anti_logged_in') != '1':
            raise SessionError('You are not logged in')
        # Getting necessary tokens and hashes
        r = self.http.get(f'{self.server}')
        soup = create_soup(r.text)
        xf_token = soup.find('input', attrs={'name': '_xfToken', 'type': 'hidden'})['value']
        # Logging out
        self.http.get(
            f'{self.server}/logout/',
            params={'_xfToken': xf_token}
        )

    def make_post(self, thread, message):
        if self.http.cookies.get('anti_logged_in') != '1':
            raise SessionError('You are not logged in')
        # Getting necessary tokens and hashes
        r = self.http.get(f'{self.server}/threads/{thread}/page-1')
        soup = create_soup(r.text)
        xf_token = soup.find('input', attrs={'name': '_xfToken', 'type': 'hidden'})['value']
        attachment_hash = soup.find(
            'input',
            attrs={'name': 'attachment_hash', 'type': 'hidden'}
        )['value']
        # Posting the message
        url = f'{self.server}/threads/{thread}/add-reply'
        r = self.http.post(
            url,
            data={
                'message_html': '<p>{}</p>'.format(message),
                '_xfToken': xf_token,
                'attachment_hash': attachment_hash,
                '_xfNoRedirect': 1,
                '_xfResponseType': 'json'
            }
        )
        result = r.json()
        if ('_redirectMessage' in result) and\
           (result['_redirectMessage'] == 'Your message has been posted.'):
            match = re.match(
                r'https://forum.antichat\.ru/posts/(\d+)',
                result['_redirectTarget']
            )
            if match is not None:
                post_id = int(match.group(1))
                return post_id
            else:
                return False
        else:
            return False

    def delete_post(self, post_id, reason=None):
        if self.http.cookies.get('anti_logged_in') != '1':
            raise SessionError('You are not logged in')
        # Getting necessary tokens and hashes
        r = self.http.get(f'{self.server}/posts/{post_id}/')
        soup = create_soup(r.text)
        xf_token = soup.find('input', attrs={'name': '_xfToken', 'type': 'hidden'})['value']
        # Deleting the post
        url = f'{self.server}/posts/{post_id}/delete'
        r = self.http.post(
            url,
            data={
                'reason': reason,
                'hard_delete': 0,
                '_xfConfirm': 1,
                '_xfToken': xf_token,
                '_xfNoRedirect': 1,
                '_xfResponseType': 'json'
            }
        )
        result = r.json()
        if ('_redirectMessage' in result) and\
           (result['_redirectMessage'] == 'Your changes have been saved.'):
            return True
        else:
            return False

    def get_reader(self, thread):
        """Returns Antichat thread reader
        @thread — Antichat thread ID
        """
        return ThreadReader(thread, self.http, self.server)
