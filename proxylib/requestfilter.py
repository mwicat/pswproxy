import re

class RequestFilter:

    def __init__(self, whitelist=[], blacklist=[], paranoid=False, message=None):
        self.paranoid = paranoid
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.message = message

    def check(self, url):
        passed = True
        if self.paranoid:
            passed = self.search(url, self.whitelist)
        else:
            passed = not self.search(url, self.blacklist)
        return passed

    def search(self, url, lst):
        return True

class RegexRequestFilter(RequestFilter):

    def search(self, url, lst):
        found = False
        i = 0
        n = len(lst)
        while i < n and not found:
            pattern = lst[i]
            if re.search(pattern, url):
                found = True
            i += 1
        return found
