import os
import subprocess
import argparse
from lxml import etree
import socket

"""Argparse for terminal execution"""
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--domain", required=True, help="Target domain to search.")
ap.add_argument("-o", "--output", required=True, help="Output file path to write results into a CSV file.")
ap.add_argument("-k", "--keep", action='store_true', help="Keep files that obtained while the program execution.")
ap.add_argument("-i", "--install", action='store_true', help="Install all modules of Recon-Ng.")
args = vars(ap.parse_args())
"""END argparse for terminal execution"""


class sublist3r:
    def __init__(self, target_domain):
        self.target_domain = target_domain

    def sublist3rFunc(self):
        """For Sublist3r Automatization: It scan results for target domain and save them into a file"""
        output_list = []

        if os.path.exists('Sublist3r'):
            path = os.path.abspath('Sublist3r')
            subprocess.run(["python3", path + "/sublist3r.py", "-d", self.target_domain, "-o", "sublist3r_" +
                            self.target_domain.split(".")[0] + ".txt"])
            with open("sublist3r_" + self.target_domain.split(".")[0] + ".txt") as txt:
                for line in txt:
                    output_list.append(line)
            return output_list

        else:
            subprocess.run(["git", "clone", "https://github.com/aboul3la/Sublist3r.git"])
            path = os.path.abspath('Sublist3r')
            subprocess.run(["python3", path + "/sublist3r.py", "-d", self.target_domain, "-o", "sublist3r_" +
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
        """For Recon-ng Automatization: It uses two modules of Recon-ng for 
        subdomain scan and save results into a file """

        ''' !!!
        # create workspace named domain 
        #subprocess.run(["recon-cli", "-w", self.target_domain.split(".")[0]])
        '''

        if args["install"]:
            os.system("recon-cli -C \" marketplace install all\" ")
        else:
            pass

        # Executing the hackertarget module for the target domain
        subprocess.run(["recon-cli", "-m", "hackertarget", "-c", "options set SOURCE " + self.target_domain, "-x"])
        subprocess.run(["recon-cli", "-m", "hackertarget", "-c", "options unset SOURCE " + self.target_domain, "-x"])

        # Executing the brute_hosts module for the target domain
        subprocess.run(["recon-cli", "-m", "brute_hosts", "-c", "options set SOURCE " + self.target_domain, "-x"])
        subprocess.run(["recon-cli", "-m", "brute_hosts", "-c", "options unset SOURCE " + self.target_domain, "-x"])

        # Load the reporting module, setting the file name and selecting hosts table from results of recon-ng,
        # then execute the module
        subprocess.run(["sudo", "recon-cli", "-m", "reporting/list",
                        "-c", "options set FILENAME " + os.getcwd() + "/recon-ng_" + self.target_domain.split(".")[
                            0] + ".txt",
                        "-c", "options set TABLE hosts",
                        "-c", "options set COLUMN host",
                        "-x"])

        # db delete hosts 0 - 1000 / Deletes domains from hosts table with range
        subprocess.run(["recon-cli", "-C", "db delete hosts 0 - 1000 ", "-x"])

        '''
        # remove workspace named domain !!!
        # subprocess.run(["recon-cli", "-C", "\"workspaces remove " + self.target_domain.split(".")[0]+"\""])
        '''

        with open(os.getcwd() + "/recon-ng_" + self.target_domain.split(".")[0] + ".txt") as txt:
            for line in txt:
                output_list.append(line)

        return output_list


class the_harvester:
    def __init__(self, target_domain):
        self.target_domain = target_domain

    def the_harvester_parser(self, input_file, output_file):
        """Accepts the output produced by theHarvester in xml format
        and then extracts subdomains and returns them as a list """

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
                                               "theharvester_" + self.target_domain.split(".")[0] + "_parsed.txt")

            os.chdir('..')
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
                                               "theharvester_" + self.target_domain.split(".")[0] + "_parsed.txt")

            os.chdir('..')
            return parsed


class MergeFinalize:
    def __init__(self, target_domain, output_file):
        self.target_domain = target_domain
        self.output_file = output_file
        self.subdomain_list = []

        # Create objects
        self.the_harvester_object = the_harvester(self.target_domain)
        self.sublist3r_object = sublist3r(self.target_domain)
        self.recon_ng_object = recon_ng(self.target_domain)

        # Create lists
        self.lst_sublistl3r = self.sublist3r_object.sublist3rFunc()
        self.lst_recon_ng = self.recon_ng_object.recon_ngFunc()
        self.lst_the_Harvester = self.the_harvester_object.the_harvesterFunc()

    def merge_lists(self):
        with open(os.path.dirname(__file__) + self.target_domain.split(".")[0] + "_joined_list.txt", "w") as wp:
            joined = self.lst_sublistl3r + self.lst_the_Harvester + self.lst_recon_ng
            joined = [each.strip() for each in joined]
            joined = set(joined)
            for sub_dom in joined:
                wp.write("{}\n".format(sub_dom))
            self.subdomain_list = joined

    def domain_ip_dict(self):

        dictionary = {}
        for domain in self.subdomain_list:
            try:
                ip = socket.gethostbyname(domain.strip())
                dictionary.update({str(domain): ip})
            except:
                dictionary.update({str(domain): "not found"})
        for x in dictionary.keys():
            print(x, ",", dictionary[x])
        return dictionary

    def write_csv(self, dictionary, result_path):

        """ Last working directory was theHarvester. Go to parent directory
            with '..'. So program is able to write output.csv to main directory. """

        with open(result_path + ".csv", "w") as wr:
            for key, value in dictionary.items():
                print(key, ",", value, file=wr)

    def combiner(self):

        self.merge_lists()
        domain_ip_dict = self.domain_ip_dict()
        self.write_csv(domain_ip_dict, self.output_file)


if __name__ == '__main__':
    domain = args["domain"]
    output = args["output"]

    merger = MergeFinalize(domain, output)
    merger.combiner()

    # Before deletion, check for the files' destination
    if args["keep"]:
        pass
    else:
        # working directory is parent directory. To delete files in theHarvester,
        # go in subdirectory
        subprocess.run(["rm", os.getcwd() + "/" + domain.split(".")[0] + "_joined_list.txt"])
        subprocess.run(["rm", os.getcwd() + "/theHarvester/theharvester_" + domain.split(".")[0] + ".xml"])
        subprocess.run(["rm", os.getcwd() + "/theHarvester/theharvester_" + domain.split(".")[0] + ".html"])
        subprocess.run(["rm", os.getcwd() + "/theHarvester/theharvester_" + domain.split(".")[0] + "_parsed.txt"])
        subprocess.run(["rm", os.getcwd() + "/sublist3r_" + domain.split(".")[0] + ".txt"])
        subprocess.run(["sudo", "rm", os.getcwd() + "/recon-ng_" + domain.split(".")[0] + ".txt"])
