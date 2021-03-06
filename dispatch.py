from functools import wraps  # so decorators don't swallow docstrings

import hexchat as hc
from tabulate import tabulate  # for outputting pretty tables

# Globals
__module_name__ = "dispatch"
__module_version__ = "0.0.1"
__module_description__ = "Assist with automating trivial FuelRat dispatch interactions"
database = {}
verbose_logging = False  # if you want to see everything, it can be deafening.
# Debug constants
debug_constant_a = [':DrillSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#DrillRats3', ":ClientName's", 'case', 'opened', 'with:', '"sol', 'pc"', '(Case', '4,', 'PC)']
debug_constant_B = [':DrillSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#DrillRats3', ":Potato's", 'case', 'opened', 'with:', '"ki', 'ps"', '(Case', '9,', 'PS4)']
debug_constant_C = ['\x0329RatMama[BOT]', 'Incoming Client: Azrael Wolfmace - System: LP 673-13 - Platform: XB - O2: OK - Language: English (English-US) - IRC Nickname: Azrael_Wolfmace', '&']
rsig_message = [':MechaSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#fuelrats', ':RATSIGNAL', '-', 'CMDR', '\x02dan8630\x02', 'potato', '-', 'System:', '\x02Praea', 'Euq', 'PI-B', 'c11\x02', '(377.53', 'LY', 'from', 'Sol)', '-', 'Platform:', '\x02PC\x02', '-', 'O2:', 'OK', '-', 'Language:', 'English', '(en-US)', '(Case', '#4)']
ps_risg_message = [':MechaSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#fuelrats', ':RATSIGNAL', '-', 'CMDR', '\x02Rawbird\x02', '-', 'System:',
                  '\x02OOCHOST', 'FD-N', 'A75-0\x02', '(not', 'in', 'EDDB)', '-', 'Platform:',
                  '\x02\x0312PS4\x03\x02', '-', 'O2:', 'NOT OK', '-', 'Language:', 'German', '(de-DE)', '(Case', '#2)']
xb_rsig_message = [':MechaSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#fuelrats', ':RATSIGNAL', '-', 'CMDR', '\x02XX', 'SAM', 'JR', 'XX\x02', '-', 'System:', '\x02CRUCIS', 'SECTOR', 'BQ-P', 'A5-1\x02', '(24.01', 'LY', 'from', 'Fuelum)', '-', 'Platform:', '\x02\x0303XB\x03\x02', '-', 'O2:', 'OK', '-', 'Language:', 'English', '(en-US)', '-']
clear_msg = [':MechaSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#fuelrats', ':Case', 'Potato', 'FrozenDemon', 'got', 'cleared!']
hc.prnt("\0033=============\n\0033custom module dispatch.py loading!\n\0033* Author:theunkn0wn1\n\0034---------")
# Decorators


def eat_all(wrapped_function):
    """:returns hc.EAT_ALL at end of wrapped function"""
    @wraps(wrapped_function)  # prevents decorator from swallowing docstrings
    def wrapper(arg,*args, **kwargs):  # todo: learn why this doesn't munch arguments
        wrapped_function(arg, args, kwargs)
        return hc.EAT_ALL
    return wrapper


def required_args(num, is_strict=False):
    def decorator(my_function):
        def fun_wrapper(*func_args):
            log("[DEBUG]", func_args[0])
            log("[DEBUG]", len(func_args[1]))
            if len(func_args[1]) == num+1:
                my_function
            elif len(func_args[1]) >= num+1 and not is_strict:
                my_function(func_args)
            else:
                print("argument mismatch. Got {} expected {}".format(len(func_args[1]), num))
                return -1
        return fun_wrapper
    return decorator


def log(trace, msg, verbose=False):
    global verbose_logging
    if verbose_logging:
        print("[{Stack}:{trace}]\t{message}".format(Stack=__module_name__, message=msg, trace=trace))
    elif verbose:
        print("[{Stack}:{trace}]\t{message}".format(Stack=__module_name__, message=msg, trace=trace))


class Translations:
    """container for translations"""

    class English:
        """Container for English facts"""
        fr = {
            'pre': "Please add the following rats to your friends list: {rats}",
            'fact': "!{platform}fr {client}"
        }
        wr = {
            'pre': "Now, please invite your rats to the wing.",
            'fact': "!{platform}wing {client}"
        }
        wb = {
            'pre': "lastly, please blind us with your beacon!",
            'fact': "!{platform}beacon {client}"
        }
        clear = {
            'pass': "{client} please stick around with your rats for some useful tips!",
            'fail':
                {
                    '+': "{client} Im sorry we could not get you in time. please stick with your rats to learn some"
                                 "useful tips as to avoid happening again",
                    '-': "{client}, Im sorry we could not get you in time, if you could please join us in"
                                 "#debrief our rats can give you some great advise as to avoid this happening again."
                                 "\n you can do so by typing '/join #debrief ' "
                }

        }

        
class Case:
    """
    Stores a case
    """
    def __init__(self, client=None, index=None, cr=False, platform=None, rats=None, system=None,stage=0, language=None,
                 raw=None):
        self.client = client
        self.index = index
        self.platform = platform
        self.cr = cr
        self.rats = rats
        self.stage = stage
        self.language = language
        self.wing = False
        self.has_forwarded = False
        self.system = system
        self.raw = raw  # debug symbol

    def __contains__(self, item):
        if item is None:
            return False
        elif item == self.client:
            return True
        elif item == self.index:
            return True
        elif item in self.rats:
            return True


class Utilities:
    @staticmethod
    def play_beep():
        """PLay a sound"""
        pass

    @staticmethod
    def strip_fancy(word, allowed_fancy=None):
        """
        Strips non alphanumeric values from a string
        :param word: word to strip
        :param allowed_fancy: non-alpha numeric characters to preserve
        :returns ret: sanitized string
        """
        ret = ""
        for char in word:
            if char.isalpha() or char.isnumeric():
                ret += char
            elif allowed_fancy is not None and char in allowed_fancy:
                ret += char
        return ret


def on_message_received(*args):
    phrase = args[0]
    channel = phrase[2]
    sender = phrase[0]
    try:

        if sender == ":MechaSqueak[BOT]!sopel@bot.fuelrats.com" or sender == ':DrillSqueak[BOT]!sopel@bot.fuelrats.com':
            log("on_message_received", phrase)
            parsed_data = Parser.parse(data=phrase)
            if parsed_data is not None:
                log("on_message_received", "parsed data is {}".format(parsed_data))
                if isinstance(parsed_data, Case):
                    Tracker.append(data=parsed_data)
                elif isinstance(parsed_data, str):
                    log("on_message_received", "case clear message\ndata is {}".format(parsed_data))
                    for key in database:
                        entry = database.get(key)
                        # entry:Case
                        if entry.client == parsed_data:
                            log("on_message_received", "found a matching case!")
                            database.pop(key)
                            break
                            # return True
                        log("on_message_received", "no matching client.")
                        # return False
            # if phrase[3] == ':RATSIGNAL':
            #     log("on_message_received", "Rsig received.")
            #     output = Parser.parse_ratsignal(phrase)
            #     log("on_message_received", "capture data is {}".format(output))
            #     Tracker.append(data=output)
        else:
            pass
            # log("on_message_received", 'not the expected user')
    except Exception as e:
        log("on_message_received", 'some error occurred! Error is as follows:\n{}'.format(e))
    # return hc.EAT_PLUGIN


class Parser:
    """
    Contains methods to parse incoming data. use .parse()
    """
    @staticmethod
    def parse_inject(capture):
        """Parses inject message events"""
        log("parse_inject", "parsing capture event with data: {}".format(capture))
        # [':DrillSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#DrillRats3', ":ClientName's", 'case', 'opened',
        #  'with:', '"sol', 'pc"', '(Case', '3,', 'PC)']
        if capture is None:
            log("parse_inject", "Invalid capture event")
        elif capture[0] != ':DrillSqueak[BOT]!sopel@bot.fuelrats.com' and capture[0] != ':MechaSqueak[BOT]!sopel@bot.fuelrats.com':
            log("parse_inject", " invalid capture event")
        else:
            log("parse_inject", 'Beginning parse attempt')
            i = 0
            # client = inject_args['client']
            # platform = inject_args['system']
            case = -1
            log("step1", 'completed!')
            client = platform = None  # init before use
            for phrase in capture:
                if phrase == 'PC)' or phrase == 'PS4)' or phrase == 'XB)':
                    log('step2', 'searching for platform...')
                    platform = phrase.strip(')')
                    log('step2', 'platform is {}'.format(platform))
                elif phrase[:5] == 'case':
                    log('step3', 'looking for client name...')
                    parsed_string = capture[i - 1]  # phrase before is the client name
                    parsed_string = parsed_string[:len(parsed_string) - 2]  # strip the 's from the end
                    parsed_string = parsed_string.strip(':')  # and the : from the start
                    client = parsed_string  # And we have our product!
                    log('step3', 'client is {}'.format(client))
                elif phrase == "(Case":
                    log('step4', 'searching for CaseID...')
                    case = capture[i + 1].strip(',')
                    log('step4', 'cid is {CID}'.format(CID=case))
                else:
                    # log("failed:", "word not read: {}".format(phrase))
                    pass
                i += 1
            # log("parse_inject", "append({},{},{},{},{})".format(case, client, platform, False, 'En-us'))
            return Case(client, case, platform=platform)

    @staticmethod
    def parse_ratsignal(phrase):
        """
        parses ratsignal events
        """
        i = 0
        client = platform = lang = cr = cid = system = None  # init before use.. prevent potential errors
        for word in phrase:
            cleaned_word = hc.strip(word)
            if cleaned_word == "CMDR":
                z = i + 2
                client = Utilities.strip_fancy(phrase[i + 1])
                while phrase[z] != "-":
                    client += "_"  # as IRC turns spaces into underscores
                    client += Utilities.strip_fancy(phrase[z])
                    z += 1

            elif cleaned_word == 'Platform:':
                platform = Utilities.strip_fancy(phrase[i + 1])
                if platform == "12PS4" or platform == "03XB":
                    platform = platform[2:]  # strip the colour code

            elif cleaned_word == "Language:":
                lang = Utilities.strip_fancy(phrase[i + 2])  # fetch the lang code

            elif cleaned_word == "O2:":
                log("parser:parse_ratsignal", "o2 is {}".format(phrase[i+1]))
                cr = phrase[i + 1]
                if cr == 'OK':
                    cr = False
                else:
                    cr = True
            elif cleaned_word == "(Case":
                cid = phrase[i + 1].strip("#").strip(")")

            elif cleaned_word == "System:":
                z = i + 1
                system = ""
                while phrase[z] != "-":
                    if "(" in phrase[z] or "not" in phrase[z]:  # checks if we have reached the distance from part of the system
                        break  # and discard, since it is not part of the actual system name
                    else:
                        system += " "
                        system += Utilities.strip_fancy(phrase[z], allowed_fancy="-")
                        z += 1
                # system.find()
            i += 1
        if cid is None:
            cid = -1  # error handling, so the case can still be deleted
        # return Case(client, cid, cr, platform, stage=0)
        return Case(client=client, index=cid, cr=cr, platform=platform, system=system, language=lang, raw=phrase)
        # return {'client': client, 'platform': platform, 'cr': cr, "case": cid, "lang": lang,
        #                 'system': system, 'stage': 0}

    @staticmethod
    def parse_clear(**kwargs):
        # [':MechaSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#fuelrats', ':Case', 'Slate_gorgon', 'got', 'cleared!']
        data = kwargs['data']
        is_valid = False
        client = None
        if data is not None or "":
            i = 0
            for word in data:
                if word == ":Case":
                    log("parse_clear", "found client name")
                    client = data[i+1]
                    log("parse_clear", "client is {}".format(client))
                elif word == "got" and data[i+1] == "cleared!":
                    is_valid = True
                i += 1
            return client if is_valid else None

    @staticmethod
    def parse_cr(**kwargs):
        i = 0
        client = None
        #  [':DrillSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#DrillRats3', ':CODE', 'RED!', 'rowdy0452', 'is', 'on', 'emergency', 'oxygen.']
        data = kwargs['data']
        for word in data:
            if Utilities.strip_fancy(word).lower() == 'code' and Utilities.strip_fancy(data[i+1]).lower() == "red":
                client = data[i+2]
            i += 1
        case = Tracker.get_case(value=client)
        case.cr = True
        return case

    @staticmethod
    def parse(**kwargs):
        """Attempts to parse incoming data,
        :returns bool or Case object
        """
        # [':MechaSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#fuelrats', ':tonyg940:', 'To', 'add', 'th
        data = kwargs['data']
        event_type = data[3]  # What kind of input
        if event_type == ":RATSIGNAL":
            return Parser.parse_ratsignal(data)
        elif Utilities.strip_fancy(event_type).lower() == "case":
            return Parser.parse_clear(data=data)
        elif event_type[-2:] == "'s":  # injected cases open with "{client}'s"
            log("Parse.part", "event type = {}".format(event_type))
            return Parser.parse_inject(data)
        elif Utilities.strip_fancy(event_type).lower() == "code":
            return Parser.parse_cr(data=data)
        else:
            log("Parser.parse", "Unknown phrase.")
            return None


class Tracker:
    """Handles case storage and handling"""
    def __init__(self):
        global database
        log("Tracker", "Initializing database...")
        database = {}

    @staticmethod
    @eat_all
    def readout(*args):
        headers = ["#", "Client", "Platform", "cr", "system", "Assigned rats"]
        data = []
        # print("readout\t",database)
        # log("readout", "- Index - | - client- | - platform - |- - - - - System - - - - -| - - - - Rats - - - -")
        for key in database:
            case = database.get(key)
            # case: Case

            data.append([key, case.client, case.platform, case.cr, case.system, case.rats])
        log("readout", tabulate(data, headers, "grid", missingval="<ERROR>"), True)
        # print("readout", database)

    @staticmethod
    @eat_all
    def debug_print(*args):
        global database
        for key in database:
            data = database.get(key)
            log("debug_print", "{key}:{data}".format(key=key, data=data.raw))

    @staticmethod
    def inject(list_arguments, from_capture=False, capture_data=None):
        """Generates a new case via  !inject and via ratsignal text events"""
        if list_arguments is None or len(list_arguments) < 3:
            pass  # not enough arguments
        else:
            try:
                prefix = list_arguments[3]
                if prefix.lower() == ":RATSIGNAL".lower():
                    log("inject", "ratsignal is present")
            except Exception as e:
                pass
            # inject_args = {'client': list_arguments[1], 'system': list_arguments[3], 'platform': list_arguments[2]}
            # order: client, platform, system
            # hc.command("say !inject {} {} {}".format(inject_args['client'], inject_args['platform'],
            #                                          inject_args['system']))
            pass

        if from_capture:
            if capture_data is None or capture_data == "":
                log("Tracker", "[FAIL]\t capture_data was None or was blank")
            else:
                log('is_capture_check', 'PASSED')
                try:
                    log("from_capture", "capture_data={}".format(capture_data))
                    if capture_data[3] == ":RATSIGNAL":
                        log("from_capture", "parse_ratsignal returned:")
                        Tracker.append(data=Parser.parse_ratsignal(capture_data))
                    else:
                        Tracker.append(data=Parser.parse_inject(capture_data))
                except Exception as e:
                    log("[FATAL]", "an error occured as follows:\n {error}".format(error=e))
                    raise e
        else:
            log("Tracker", "not capture data")

    @staticmethod
    def append(**kwargs):
        """Appends a new entry to the db
        expected: None,id,client,system,platform,cr,language
        """

        log('toggle_verbose', "args =\t{}".format(kwargs))
        data = kwargs['data']
        if isinstance(data, Case):  # Sanity check. Writing a non-class object would be... less than ideal
            new_entry = {int(data.index): data}
            log("append", "new entry is {}".format(new_entry))
            database.update(new_entry)
            log("append", "new entry created...")
            return 1
        else:
            log("append", "data is NOT of type Case!")
            return 0

    @staticmethod
    @eat_all
    def rm(word, word_eol, user_data):
        log("rm", "removing case with CID {}...".format(word[1]))
        try:
            cid = int(word[1])
            if database.pop(cid, None) is None:
                log("rm", "Failed to remove {cid}, no such case {cid}.".format(cid=cid), True)
                log("rm", "raw dict is{}".format(database))
                return False
            else:
                # print(database)
                log("rm", "successfully removed case {}".format(cid), True)
                return False
        except Exception as e:
            log("rm", "unable to remove case {}. An unknown error occurred.".format(cid), True)
            log("rm", "Exception is: {}".format(e))
            return False

    @staticmethod
    def get_case(**kwargs):
        value = kwargs['value']
        for key in database:
            obj = database.get(key)
            # obj: Case
            if value in obj:
                return obj
        return None

    @staticmethod
    def change_system(**kwargs):
        i = kwargs['case']
        system = kwargs['system']
        case = database.get(int(i))
        # case: Case
        case.system = system
        log("change_system", "case c{id} {client} was updated to {system}".format(id=case.index,client=case.client,
                                                                                  system=case.system))


class Commands:
    """contains the Commands invoked via slash hooked during init"""

    @staticmethod
    @eat_all
    def client_name():
        pass

    @staticmethod
    @eat_all
    def system(word, word_eol, userdata):
        case = word[1]
        log("system", "type of word_eol is  {} with data {}".format(type(word_eol), word_eol))
        system = word_eol[0][2]  # assuming anything after the case number is part of the system...
        Tracker.change_system(case=case, system=system)

    @staticmethod
    @eat_all
    def toggle_verbose(*args):
        global verbose_logging
        verbose_logging = not verbose_logging
        log("toggle_verbose", "Toggling verbose logging to {}".format(verbose_logging), True)

    @staticmethod
    @eat_all
    def run_tests(word, word_eol, userdata):
        """Runs tests and generates some dummy cases"""
        log("run_tests", "Running Tracker.inject Test 1...")
        Tracker.inject([None], True, None)
        # log("run_tests", "running test 2")
        # print(Tracker.inject([None, 'clientName', 'systemName', 'PC'], True, debug_constant_a))
        log('run_tests', 'running test 3')

        Tracker.inject([None, None, None], True, debug_constant_B)
        # assert not Tracker.rm([None, 9], None, None)  # if we can't remove the case - it didn't get formed as expected

        log('run_tests', "Running pc rsig...")
        Tracker.inject([None, None, None], True, rsig_message)
        # assert not Tracker.rm([None, 4], None, None)

        log("run_tests", 'Running pc rsig via on_message_received...')
        on_message_received(rsig_message, None, None)
        on_message_received(ps_risg_message)
        log("run_tests", "running xb rsig via on_message_received")
        on_message_received(xb_rsig_message)
        log("run_tests", "testing clear...")
        on_message_received(clear_msg)

        log("run_tests", "done!")

    @staticmethod
    @eat_all
    def oxy_check(a, b, c):
        name = "oxy_check"
        log(name, "checking o2 for client:\t{cmdr}".format(cmdr=a[1]))
        hc.command("say greetings " + a[1] + ",are you on emergency o2?(blue timer top right)")

    @staticmethod
    @eat_all
    def oxy_ack(a, b, c):
        name = "oxyAck"
        log(name, "ackowledging OK o2")
        commander = a[1]
        hc.command("say {}, Understood, please let me know at once if it makes itself known ;)".format(commander))

    @staticmethod
    @eat_all
    def print_test(a, b, c):
        print("a=\t{}".format(a))
        print("b=\t{}".format(b))
        hc.command("msg TNTom[PC] " + a[1])

    @staticmethod
    @eat_all
    def inject_case(x, y, z):
        name = "injectCase"
        log(name, "Injecting case")
        subject = x[1]
        sys = x[2]
        platform = x[3]
        hc.command("say !inject {} {} {}".format(subject, sys, platform))

    @staticmethod
    @eat_all
    def go(x, y, z):
        name = "go"
        case = x[1]
        rat = x[2]
        client = x[3]
        log(name, "Giving {} the go signal for case {}".format(rat, case))
        hc.command("say {} please add the following rat to your friends list".format(client))
        hc.command("say !go {cid} {rat}".format(cid=case, rat=rat))
        # time.sleep()
        hc.command("say !pcfr {}".format(client))

    @staticmethod
    @eat_all
    def clear(a, b, c):
        """ Reminds client to remain with their rats for the DB, then clears the case with Mecha
        expected order of a: id,rat,client
        """
        name = "clear"
        entry = database.get(a[1])
        commander = entry['client']

        case = a[1]
        rat = a[2]
        log(name, "Commander= \"{x}\",Case \"{y}\",rat \"{z}\"".format(x=commander, y=case, z=rat))
        hc.command("say {cmdr} ,please stick with your rat(s) for a moment to learn some useful tips! ;)".format(
            cmdr=commander))
        hc.command("say !clear {case} {rat}".format(case=case, rat=rat).format(case=case, rat=rat))

    @staticmethod
    @eat_all
    def clear_drill(a, b, c):
        name = "clear"
        commander = a[2]
        case = a[1]
        log(name, "Commander= \"{x}\",Case \"{y}\"".format(x=commander, y=case))
        hc.command("say {cmdr} ,please stick with your rat(s) for a moment to learn some useful tips! ;)".format(
            cmdr=commander))
        hc.command("say !clear {case}".format(case=case))

    # ['\x0324Helitony[XB]', 'Comms+ for EldestDrifter']
    # target element is the [1] element, will have to parse the hard way. Need that string first
    @staticmethod
    @eat_all
    def print_hook(x, y, z):
        log("print_hook", hc.strip(x[1]))
        print(x)
        print(y)

    @staticmethod
    @eat_all
    def server_hook(x, y, z):
        log("server_hook", x)

    @staticmethod
    @eat_all
    def generic_msg(x, y, z):
        log("generic_msg", x)

    @staticmethod
    @eat_all
    def change_index(word, word_eol, event_args):
        key = word[1]
        log("change_index", " key is {}".format(key))
        new_key = word[2]
        case = database.pop(int(key))
        case.index = int(new_key)
        Tracker.append(data=case, index=new_key)

    @staticmethod
    @eat_all
    def stage(x, y, z):
        # todo make invalid argument count not break things
        event_args = [None]*3
        print("len(X) = {}".format(len(x)))
        if len(x) < 1:
            log('stage', 'expected format /stage {index} {mode} {param}')
        elif len(x) == 3: # no extra arguments
            pass
        else:
            mode = x[2]
            log("stage", "mode = {} and is of type {}".format(mode, type(mode)))
            cid = int(x[1])
            try:  # if we have extra args
                event_args[0] = x[3]
                event_args[1] = x[4]
                event_args[2] = x[5]
                log("\0034stage\003", "event_args={}".format(event_args))
            except IndexError:  # but less than 3
                try:
                    log("stage", "two extra arguments")
                    event_args[0] = x[3]
                    event_args[1] = x[4]
                except IndexError:  # only one extra argument
                    try:
                        log("stage", "only one extra argument?")
                        event_args[0] = x[3]
                    except Exception as e:  # erm.. well this was not planned for
                        log("stage", "\0034Well something went very wrong.", True)
                        log("stage", e, True)  # TODO  investigate a crash in here
            log("stage", "=======================")
            log("stage event_args=", event_args)
            if StageManager.do_stage(cid, mode, alpha=event_args[0], beta=event_args[1], gamma=event_args[2]):
                pass
            else:
                log("stage", 'unknown mode {}'.format(mode))
        # log("stage", 'current stage is {stage}'.format())


class StageManager:
    """Tracks client stage and responds accordingly"""
    @staticmethod
    def say(message, colour=None):
        """Output a message into the channel (*this is server-side!*)"""
        if colour is None:
            hc.command("say {msg}".format(msg=message))
        else:
            hc.command("say \003{color} {msg}".format(color=colour, msg=message))

    @staticmethod
    def change_platform(key, platform, case_object):
        """Changes a client's platform
        :param key: database key for client
        :param platform: new platform
        :param case_object: clients case object
        """
        global database
        if platform == 'ps' or platform == 'pc' or platform == 'xb':
            # formed_dict: Case  # technicially this isn't used, but will need to be removed before executing!

            formed_dict = case_object  # since hex forces usage of 3.5 rather than 3.6...
            formed_dict.platform = platform
            log('change_platform', "Successfully updated platform for case {}".format(key),True)

    @staticmethod
    def friend_request(case_object):
        """Tells client to add rat(s) to friends list"""
        # case_object: Case  # todo remove this line
        platform = case_object.platform
        client = case_object.client
        if case_object.language.lower() == 'enus':
            # StageManager.say(Translations.English.fr['pre'].format(rats=case_object['rats']))  # TODO make work
            log("friend_request", "triggered!", True)
            StageManager.go(case_object, None)
            StageManager.say(Translations.English.fr['fact'].format(client=client, platform=platform))
        log("friend_request", "Client {client} is on platform {platform} with lang {lang}"
            .format(client=client, platform=platform, lang=case_object.language), True)
        # TODO: implement other languages, add option to outsource facts to Mecha

    @staticmethod
    def wing_invite(case_object):
        # case_object: Case  # todo rm this line
        if case_object['language'] == 'English-us':
            StageManager.say(Translations.English.wr['pre'], '03')
            StageManager.say(Translations.English.wr['fact'].format(client=case_object.client, platform=
                                                                    case_object.platform), '03')
            # TODO: implement other languages,
            # TODO: implement Mecha facts

    @staticmethod
    def wing_beacon(case_object):
        if case_object['language'] == 'English-us':
            # case_object: Case  # todo rm this line
            StageManager.say(Translations.English.wb['pre'], '03')
            StageManager.say(Translations.English.wb['fact'].format(client=case_object.client, platform=
                                                                    case_object.platform), '03')
        # TODO implement other languages and implement Mecha interaction

    @staticmethod
    def fail(case_object):
        # case_object: Case  # todo rm this line
        if case_object['wing']:
            StageManager.say(Translations.English.clear['fail']['+'].format(client=case_object.client))
        else:
            StageManager.say(Translations.English.clear['fail']['-'].format(client=case_object.client))

    @staticmethod
    def wing_conf(case_object):
        case_object.wing = True

    @staticmethod
    def check_o2(case_object):
        StageManager.say("Greetings {client}, are you on emergency oxygen? (blue countdown timer top right)?".format(
            client=case_object.client))

    @staticmethod
    def add_rats(case_object, rats):
        """Adds up to 3 rats to a given case
        :param case_object: case to update
        :param rats: list of rats to add
        """
        # TODO make multiple rats actually work
        try:
            log("\0034add_rats\003", "rats = {}".format(rats))
            case_object.rats.update({0: rats[0]})
            case_object.rats.update({1: rats[1]})
            case_object.rats.update({2: rats[2]})
            print(case_object.rats)
            log("add_rats", "rats added", True)
        except Exception as e:
            log('add_rats', "an error occurred!", True)
            print(e)

    @staticmethod
    def go(case_object, event_args):
        if event_args is not None:
            StageManager.add_rats(case_object, event_args)
        rats = case_object.rats if case_object.rats is not None else []  # prevent index errors (hopefully)...
        quantity_none = 0
        for rat in rats:
            if rat is None:
                quantity_none += 1
        if quantity_none == 0:
            StageManager.say("Please add {alpha},{beta},{gamma} to your friends list.".format(alpha=rats[0], beta=rats[1], gamma=rats[2]))
        elif quantity_none == 1:
            StageManager.say(
                "Please add {alpha},{beta} to your friends list.".format(alpha=rats[0], beta=rats[1]))
        elif quantity_none == 2:
            StageManager.say(
                "Please add {alpha} to your friends list.".format(alpha=rats[0]))
            StageManager.say(
                "!{platform}fr".format(platform=case_object['platform'])
            )

    @staticmethod
    @eat_all
    def do_stage(key, mode, alpha=None, beta=None, gamma=None):
        """Advances the case's stage and does the next step
        :param beta: optional extra argument, for supported functions
        :param gamma: optional extra argument, for supported functions
        :param alpha: optional extra argument, for supported functions
        :param key: Database key to use
        :param mode: dictate which method to execute
        :returns boolean success
        """
        log("do_stage", "\0034 vars are {} {} {}".format(alpha, beta, gamma))
        log("do_stage", "mode is of type {} with data".format(type(mode)))
        print(mode)
        global database
        steps = {0: StageManager.check_o2,
                 1: StageManager.friend_request,
                 2: StageManager.wing_invite,
                 3: StageManager.wing_beacon,
                 }
        # case_object: Case # todo comment line out (unrecoverable syntax error because hexchat)
        try:
            case_object = database.get(int(key))
        except Exception as e:
            log("stage", "unable to retrieve case with key {}".format(key))
            return False

        if mode == 'get' or mode == 'status':
            log('stage; [get]', 'attempting to retrieve case_object with key {} of type {}'.format(key, type(key)))

            log('stage', 'status of {CID} is:\nStage: {status}'.format(CID=int(key), status=case_object.stage), True)
            log('stage', "Platform:{platform}\tRats: {rats}".format(platform=case_object.platform,rats=case_object.rats))
            return True

        elif mode == 'up':
            steps[case_object.stage](case_object)
            case_object.stage += 1
            case_object.has_forwarded = True
            log('stage:up', 'stage set to {}'.format(case_object.stage), True)
            return True

        elif mode == 'back':
            """Steps a case back a step and issues the previous command"""
            if case_object.has_forwarded:
                case_object.stage -= 2
                case_object.has_forwarded = False
                # log('Stage:back', "Backing up..", True)
            else:
                case_object['stage'] -= 1
            steps[case_object.stage](case_object)
            return True

        elif mode == 'repeat':
            """Repeats current stage command"""
            steps[case_object.stage](case_object)
            return True

        elif mode == "fr":
            """Instructs client to add rats to friends list"""
            steps[0](case_object)
            return True

        elif mode == "wing+":
            StageManager.wing_conf(case_object)
            log("do_stage:wing+", 'writing wing status for key {}'.format(key), True)
            return True

        elif mode == 'fail':
            StageManager.fail(case_object)
            return True
        elif mode == 'platform':
            log('do_stage:platform', "writing platform {} for key {}".format(alpha, key))
            StageManager.change_platform(key, alpha, case_object)
            return True
        elif mode == 'add':
            log("do_stage:add", "adding rats {},{},{} to {}".format(alpha, beta, gamma, key))  # TODO make work with kwargs
            StageManager.add_rats(case_object, [alpha, beta, gamma])
            return True


def init():
    cmd = Commands()
    board = Tracker()
    log("Init", "Adding hooks!")
    commands = {
        'sys': cmd.system,
        'potato': cmd.print_hook,
        'test': cmd.run_tests,
        'o2': cmd.oxy_check,
        "test2": cmd.print_test,
        "clear": cmd.clear,
        "o2k": cmd.oxy_ack,
        "go": cmd.go,
        "inject": cmd.inject_case,
        "dClear": cmd.clear_drill,
        "stage": cmd.stage,
        # "new": board.append,  # yeah no, this needs to be put into a wrapper (expects dict, gets string array)
        "del": board.rm,
        'rm': board.rm,
        'md': board.rm,
        "board": board.readout,
        "verbose": cmd.toggle_verbose,
        "raw_board": Tracker.debug_print,
        "mv": cmd.change_index
    }
    try:
        for key in commands:
            log("init", "adding hook for\t{}".format(key))
            hc.hook_command(key, commands[key])
        hc.hook_server("PRIVMSG", on_message_received)

    except Exception as e:
        log("Init", "\0034Failure adding hooks! error reads as follows:", True)
        log("Init", e, True)
    else:
        log("Init", "\0033 Everything is prepared. Ready.", True)


# ['\x0329RatMama[BOT]', 'Incoming Client: Azrael Wolfmace - System: LP 673-13 - Platform: XB - O2: OK - Language: English (English-US) - IRC Nickname: Azrael_Wolfmace', '&']
if __name__ == '__main__':  # this prevents script code from being executed on import. (bad!)
    init()
