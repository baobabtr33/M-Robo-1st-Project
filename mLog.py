import logging.config


def status_checker(name, status):
    logger = logging.getLogger(name)

    if status != 200:
        status_category = str(status)[0]
        if status_category == '3':
            logger.warning("DART RSS: HTTPS status - {} - redirection".format(status))
            # continue
        elif status_category == '4':
            logger.critical("DART RSS: HTTPS status - {} - client error".format(status))
            exit()
        elif status_category == '5':
            logger.critical("DART RSS: HTTPS status - {} - server error".format(status))
            exit()
        else:
            logger.INFO("Something is wrong with RSS request. Status Code: {}".format(status))
