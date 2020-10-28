import logging.config


def status_checker(name, status):
    logger = logging.getLogger(name)

    if status != 200:
        status_category = str(status)[0]
        if status_category == '3':
            logger.error("DART RSS: HTTPS status - {} - redirection".format(status))
            # continue
        elif status_category == '4':
            logger.warning("DART RSS: HTTPS status - {} - client error".format(status))
            exit()
        elif status_category == '5':
            logger.warning("DART RSS: HTTPS status - {} - server error".format(status))

        else:
            logger.INFO("Something is wrong with RSS request. Status Code: {}".format(status))
            # continue