import os
import subprocess
import argparse
from collections import OrderedDict
from impacket.smbserver import outputToJohnFormat
from lxml import etree
import socket

'''
"""Argparse for terminal execution"""
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--domain", required=True, help="Target domain to search.")
ap.add_argument("-o", "--output", required=True, help="Output file path to write results into a CSV file.")
ap.add_argument("-k", "--keep", action='store_true', help="Keep files that obtained while the program execution.")
ap.add_argument("-i", "--install", action='store_false', help="Install all modules of Recon-Ng.")
args = vars(ap.parse_args())
"""END argparse for terminal execution"""
'''


class sublist3r:

    def __init__(self, target_domain):
        self.target_domain = target_domain

    def sublist3rFunc(self):
        """For Sublist3r Automatization: It scan results for target domain and save them into a file"""
        output_list = []
        if os.path.exists('Sublist3r'):
            path = os.path.abspath('Sublist3r')

            subprocess.run(["python3", path + "/./sublist3r.py", "-d", self.target_domain, "-o", "sublist3r_" +
                            self.target_domain.split(".")[0] + ".txt"])

            with open("sublist3r_" + self.target_domain.split(".")[0] + ".txt") as txt:
                for line in txt:
                    output_list.append(line)

            return output_list

        else:
            subprocess.run(["git", "clone", "https://github.com/aboul3la/Sublist3r.git"])
            path = os.path.abspath('Sublist3r')
            subprocess.run([path + "/./sublist3r.py", "-d", self.target_domain, "-o", "sublist3r_" +
                            self.target_domain.split(".")[0] + ".txt"])

            with open("sublist3r_" + self.target_domain.split(".")[0] + ".txt") as txt:
                for line in txt:
                    output_list.append(line)

            return output_list


class recon_ng:

    def __init__(self, target_domain):
        self.target_domain = target_domain

    def recon_ngFunc(self):
        output_list = []

        """For Recon-ng Automatization: It uses two modules of Recon-ng for subdomain scan and save results into a file"""
        # Executing the hackertarget module for the target domain
        subprocess.run(["recon-cli", "-m", "hackertarget", "-c", "options set SOURCE " + self.target_domain, "-x"])
        # Executing the brute_hosts module for the target domain
        subprocess.run(["recon-cli", "-m", "brute_hosts", "-c", "options set SOURCE " + self.target_domain, "-x"])
        # Load the reporting module, setting the file name and selecting hosts table from results of recon-ng,
        # then execute the module
        subprocess.run(["sudo", "recon-cli", "-m", "reporting/list", "-c", "options set FILENAME " + os.getcwd() +
                        "/recon-ng_" + self.target_domain.split(".")[0] + ".txt", "-c", "options set TABLE hosts",
                        "-x"])

        with open(os.getcwd() + "/recon-ng_" + self.target_domain.split(".")[0] + ".txt") as txt:
            for line in txt:
                output_list.append(line)

        return output_list


class the_harvester:

    def __init__(self, target_domain):
        self.target_domain = target_domain

    def the_harvester_parser(self, input_file, output_file):
        """Accepts the output produced by theHarvester in xml format and then extracts subdomains and returns them as a list"""

        parser = etree.XMLParser(recover=True, encoding="UTF-8")
        tree = etree.parse(input_file, parser=parser)
        root = tree.getroot()
        lines_seen = set()

        for item in root.iter('theHarvester'):
            for label in item.iter("host"):
                if label.text is None:
                    continue
                if "." in label.text:
                    lines_seen.add(label.text)
            for label in item.iter("hostname"):
                if '.' in label.text:
                    lines_seen.add(label.text)

        with open(output_file, "w") as fp:
            for each in lines_seen:
                if '\n' not in each:
                    lines_seen.add(each)
                    fp.write(each)
        return list(lines_seen)

    def the_harvesterFunc(self):

        if os.path.exists('theHarvester'):
            os.chdir("theHarvester/")

            subprocess.run(
                ["python3", "./theHarvester.py", "-d", self.target_domain, "-b", "all", "-f", "theharvester_" +
                 self.target_domain.split(".")[0]], check=True)

            parsed = self.the_harvester_parser("theharvester_" + self.target_domain.split(".")[0] + ".xml",
                                               "theharvester_" +
                                               self.target_domain.split(".")[0] + "_parsed.txt")

            return parsed

        else:
            os.system("git clone https://github.com/laramies/theHarvester.git")
            os.chdir("theHarvester/")

            # Before the first run, satisfying all the requisites
            os.system("python3 -m pip install -r requirements.txt")

            subprocess.run(
                ["python3", "./theHarvester.py", "-d", self.target_domain, "-b", "all", "-f", "theharvester_" +
                 self.target_domain.split(".")[0]], check=True)

            parsed = self.the_harvester_parser("theharvester_" + self.target_domain.split(".")[0] + ".xml",
                                               "theharvester_" +
                                               self.target_domain.split(".")[0] + "_parsed.txt")

            return parsed


class outputting:

    def __init__(self, target_domain):
        self.target_domain = target_domain

    def merge_lists(self, target_domain, lst1, lst2, lst3):
        with open(target_domain.split(".")[0] + "_joined_list.txt", "w") as wp:
            lst1, lst2, lst3 = lst_sublistl3r, lst_the_Harvester, lst_recon_ng

            joined = lst_sublistl3r + lst_the_Harvester + lst_recon_ng
            joined = [each.strip() for each in joined]
            joined = set(joined)

            for sub_dom in joined:
                wp.write("{}\n".format(sub_dom))
            return joined

    def domain_ip_dict(self, subdomain_list):
        keys = ['domain', 'ip']
        dictionary = {key: None for key in keys}

        for domain in subdomain_list:
            try:
                ip = socket.gethostbyname(domain.strip())
                dictionary.update({str(domain): ip})
            except:
                dictionary.update({str(domain): "not found"})

        for x in dictionary.keys():
            print(x, " : ", dictionary[x])

        return dictionary

    def write_csv(self, dictionary, result_path):

        with open(self.target_domain.split(".")[0] + "_output_list.txt", "w") as wr:
            for key in dictionary.keys():
                print(key, " : ", dictionary[key], file=wr)


if __name__ == '__main__':
    # domain = args["domain"]
    domain = 'gib.gov.tr'

    sublist3r_object = sublist3r(domain)
    lst_sublistl3r = sublist3r_object.sublist3rFunc()

    the_harvester_object = the_harvester(domain)
    lst_the_Harvester = the_harvester_object.the_harvesterFunc()

    # if args["install"]:
    #     subprocess.run(["recon-cli", "-C", "\"marketplace install all\""])
    # else:
    #     pass

    recon_ng_object = recon_ng(domain)
    lst_recon_ng = recon_ng_object.recon_ngFunc()

    print("---------joined list-------------")

    outputting_object = outputting(domain)
    subdomain_list = outputting_object.merge_lists(domain, lst_sublistl3r, lst_the_Harvester, lst_recon_ng)
    dict = outputting_object.domain_ip_dict(subdomain_list)

    for i in subdomain_list:
        print(i)

    for x in dict.keys():
        print(x, "=>", dict[x])

    result_path = os.getcwd()
    outputting_object.write_csv(dict, result_path)

    # args["output"]
    output = "/last_output.txt"

    # for i in joined:
    #     print(i)

    # Before deletion, check for the files' destination    
    # if args["keep"]:
    #     pass
    # else:
    #     subprocess.run(["rm", "merged_unique_subdomain_list.txt"])
    #     subprocess.run(["rm", "theharvester_" + target.split(".")[0] + ".xml"])
    #     subprocess.run(["rm", "theharvester_" + target.split(".")[0] + "_parsed.txt"])
    #     subprocess.run(["rm", "sublist3r_" + target.split(".")[0] + ".txt"])
    #     subprocess.run(["sudo", "rm", "recon-ng_" + target.split(".")[0] + ".txt"])
