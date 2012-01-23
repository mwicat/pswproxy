passed = filter.check(request)
logger.log(request, passed)
if passed:
    resp = send_request(request)
    resp = replacer.replace(resp)
    send_response(resp)
