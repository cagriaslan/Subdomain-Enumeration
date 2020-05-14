import os
import subprocess
import argparse
from collections import OrderedDict

"""Argparse for terminal execution"""
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--domain", required=True, help="Target domain to search.")
ap.add_argument("-o", "--output", required=True, help="Output file path to write results into a CSV file.")
args = vars(ap.parse_args())
"""END argparse for terminal execution"""


def main(target, result_path):
    """Scan operations"""
    sublist3r(target)
    the_harvester(target)
    recon_ng(target)
    """End of scan operations"""

    # Formatting the results and make them unique.
    merge_lists(target)
    # Writing results into a csv file.
    write_csv(result_path)


def sublist3r(target_domain):
    if os.path.exists('Sublist3r'):
        path = os.path.abspath('Sublist3r')
        sublister = subprocess.run([path + "/./sublist3r.py", "-d", target_domain, "-o", "sublist3r" +
                                    target_domain.split(".")[0] + ".txt"])
        print(sublister)
    else:
        subprocess.run(["git", "clone", "https://github.com/aboul3la/Sublist3r.git"])
        path = os.path.abspath('Sublist3r')
        sublister = subprocess.run([path + "/./sublist3r.py", "-d", target_domain, "-o", "sublist3r" +
                                    target_domain.split(".")[0] + ".txt"])
        print(sublister)


def recon_ng(target_domain):
    """For Recon-ng Automatization"""
    # Inserting domain name into recon-ng database
    subprocess.run(["recon-cli", "-C", "\"db insert domains\"" + target_domain])
    # Check the domain list
    subprocess.run(["recon-cli", "-C", "\"show domains\""])
    # Executing the hackertarget module for the target domain
    subprocess.run(["recon-cli", "-m", "hackertarget", "-x"])
    # Executing the brute_hosts module for the target domain
    subprocess.run(["recon-cli", "-m", "brute_hosts", "-x"])
    # Load the reporting module, setting the file name and selecting hosts table from results of recon-ng,
    # then execute the module
    subprocess.run(["sudo", "recon-cli", "-m", "reporting/list", "-c", "options set FILENAME " + os.getcwd() +
                    "/recon-ng.txt", "-c" "options set TABLE hosts", "-x"])


def the_harvester(target_domain):
    """For theHarvester: The file 'api-keys.yaml' must exist under the directory where the command executed"""
    harvester = subprocess.run(["theHarvester", "-d", target_domain, "-b", "all", "-f", "theharvester_" +
                                target_domain.split(".")[0] + ".xml"], check=True)
    print(harvester)
    # Returns all subdomains found by theHarvester as a list and saves it to a file
    return the_harvester_parser("theharvester_" + target_domain.split(".")[0] + ".xml", "theharvester_" +
                                target_domain.split(".")[0] + "_parsed.txt")


def the_harvester_parser(input_file, output_file):
    """Accepts the output produced by theHarvester in xml format and then extracts subdomains and returns them as a
    list"""
    import xml.etree.ElementTree as ET
    tree = ET.parse(input_file)
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
                fp.write(each + "\n")
    return list(lines_seen)


def ns_lookup(subdomain_list):
    """Expects a list of subdomains (each on a new line) and returns subdomain: IP dict"""
    ip_dom_dict = {}
    with open(subdomain_list, "r") as file:
        for subdomain in file:
            try:
                process = subprocess.run(["nslookup", subdomain.split("\n", 1)[0]], check=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, universal_newlines=True)
                output = process.stdout
                for idx, row in enumerate(output.splitlines()):
                    if idx == 4:
                        dom_name = row.split(":")[1]
                    if idx == 5:
                        ip_add = row.split(":")[1]
                        ip_dom_dict[dom_name.split("\t")[1]] = ip_add.split()[0]
            except:
                print("An error occurred for " + subdomain.split("\n", 1)[0])

    print(ip_dom_dict)
    return ip_dom_dict


def merge_lists(target_domain):
    """It takes all output files which are obtained from tools and merge them in one file without duplicates"""
    all_lines = ''
    with open("theharvester_" + target_domain.split(".")[0] + "_parsed.txt", "r") as file1:
        for subdomain in file1:
            all_lines += subdomain + "\n"
    with open("recon-ng.txt", "r") as file2:
        for subdomain in file2:
            all_lines += subdomain + "\n"
    with open("sublist3r" + target_domain.split(".")[0] + ".txt", "r") as file3:
        for subdomain in file3:
            all_lines += subdomain + "\n"
    with open("unique_list.txt", "w") as wp:
        # Eliminating the duplicate lines.
        unique_list = "\n".join(list(OrderedDict.fromkeys(all_lines.split("\n"))))
        for sub_dom in unique_list.splitlines():
            wp.write("{}\n".format(sub_dom))


def write_csv(result_path):
    """It writes the dictionary returned from ns_lookup() into a csv file with format."""
    dict_to_write = ns_lookup("unique_list.txt")
    with open(result_path, "w") as wr:
        for key in dict_to_write:
            wr.write("{},{}\n".format(key, dict_to_write[key]))


if __name__ == '__main__':
    main(args["domain"], args["output"])


