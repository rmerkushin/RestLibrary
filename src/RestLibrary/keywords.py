#!/usr/bin/env python
# -*- coding: utf-8 -*-
# rmerkushin@gmail.com

import json
from os import path
from requests import Session
from robot.api import logger
from robot.utils import ConnectionCache
from robot.libraries.BuiltIn import BuiltIn


class RestKeywords(object):

    def __init__(self):
        self._cache = ConnectionCache()
        self._builtin = BuiltIn()

    @staticmethod
    def _normalize(d):
        if type(d) is dict:
            return dict((k, RestKeywords._normalize(v)) for k, v in d.iteritems() if v and RestKeywords._normalize(v))
        elif type(d) is list:
            return [RestKeywords._normalize(v) for v in d if v and RestKeywords._normalize(v)]
        else:
            return d

    @staticmethod
    def convert_to_json(strings, normalize="False"):
        if type(strings) is list:
            json_ = map(lambda s: json.loads(s), strings)
        else:
            json_ = json.loads(strings)
        if normalize.upper() == "TRUE":
            if type(json_) is list:
                json_ = map(lambda x: RestKeywords._normalize(x), json_)
            else:
                json_ = RestKeywords._normalize(json_)
        return json_

    @staticmethod
    def convert_to_multipart_encoded_files(files):
        mpe_files = []
        for f in files:
            form_field_name = f[0]
            file_name = path.basename(f[1])
            file_path = f[1]
            mime_type = f[2]
            mpe_files.append((form_field_name, (file_name, open(file_path, "rb"), mime_type)))
        return mpe_files

    def create_session(self, alias, headers=None, auth=None, verify="False", cert=None):
        session = Session()
        if headers:
            session.headers.update(headers)
        if auth:
            session.auth = tuple(auth)
        session.verify = self._builtin.convert_to_boolean(verify)
        session.cert = cert
        self._cache.register(session, alias)

    def head(self, alias, url, params=None, headers=None, cookies=None, timeout=10):
        logger.info("Sending HEAD request to: '" + url + "', session: '" + alias + "'")
        session = self._cache.switch(alias)
        resp = session.head(url, params=params, headers=headers, cookies=cookies, timeout=timeout)
        return {"status": resp.status_code, "headers": resp.headers}

    def get(self, alias, url, params=None, headers=None, cookies=None, timeout=10):
        logger.info("Sending GET request to: '" + url + "', session: '" + alias + "'")
        session = self._cache.switch(alias)
        resp = session.get(url, params=params, headers=headers, cookies=cookies, timeout=timeout)
        try:
            return {"status": resp.status_code, "headers": resp.headers, "body": resp.json()}
        except ValueError:
            return {"status": resp.status_code, "headers": resp.headers, "body": resp.content}

    def post(self, alias, url, headers=None, data=None, files=None, cookies=None, timeout=10):
        logger.info("Sending POST request to: '" + url + "', session: '" + alias + "'")
        session = self._cache.switch(alias)
        resp = session.post(url, headers=headers, cookies=cookies, data=data.encode("utf-8"), files=files, timeout=timeout)
        try:
            return {"status": resp.status_code, "headers": resp.headers, "body": resp.json()}
        except ValueError:
            return {"status": resp.status_code, "headers": resp.headers, "body": resp.content}

    def put(self, alias, url, headers=None, data=None, cookies=None, timeout=10):
        logger.info("Sending PUT request to: '" + url + "', session: '" + alias + "'")
        session = self._cache.switch(alias)
        resp = session.put(url, headers=headers, cookies=cookies, data=data.encode("utf-8"), timeout=timeout)
        try:
            return {"status": resp.status_code, "headers": resp.headers, "body": resp.json()}
        except ValueError:
            return {"status": resp.status_code, "headers": resp.headers, "body": resp.content}

    def delete(self, alias, url, headers=None, data=None, cookies=None, timeout=10):
        logger.info("Sending DELETE request to: '" + url + "', session: '" + alias + "'")
        session = self._cache.switch(alias)
        resp = session.delete(url, headers=headers, cookies=cookies, data=data.encode("utf-8"), timeout=timeout)
        try:
            return {"status": resp.status_code, "headers": resp.headers, "body": resp.json()}
        except ValueError:
            return {"status": resp.status_code, "headers": resp.headers, "body": resp.content}

    def close_all_sessions(self):
        self._cache.empty_cache()
