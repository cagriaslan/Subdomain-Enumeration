import os
import subprocess
import argparse
from collections import OrderedDict
from lxml import etree

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
        
            subprocess.run(["python3", "./theHarvester.py", "-d", self.target_domain, "-b", "all", "-f", "theharvester_" + 
                                self.target_domain.split(".")[0] ], check=True)


            parsed =  self.the_harvester_parser("theharvester_" + self.target_domain.split(".")[0] + ".xml", "theharvester_" +
                                self.target_domain.split(".")[0] + "_parsed.txt")
            

            return parsed
            


        else:
            os.system("git clone https://github.com/laramies/theHarvester.git")
            os.chdir("theHarvester/")  

            # Before the first run, satisfying all the requisites
            os.system("python3 -m pip install -r requirements.txt")
            
            subprocess.run(["python3", "./theHarvester.py", "-d", self.target_domain, "-b", "all", "-f", "theharvester_" + 
                                self.target_domain.split(".")[0] ], check=True)
         
            parsed = self.the_harvester_parser("theharvester_" + self.target_domain.split(".")[0] + ".xml", "theharvester_" +
                                self.target_domain.split(".")[0] + "_parsed.txt")

            return parsed
            


if __name__ == '__main__': 

    #domain = args["domain"]
    domain = 'tesla.com'

    sublist3r_object = sublist3r(domain)
    lst_sublistl3r = sublist3r_object.sublist3rFunc()

    the_harvester_object = the_harvester(domain)
    lst_the_Harvester = the_harvester_object.the_harvesterFunc()


    print("---------joined list-------------")

    joined = lst_sublistl3r+lst_the_Harvester
    joined = [each.strip() for each in joined]
    joined = set(joined)

    for i in joined:
        print(i)
