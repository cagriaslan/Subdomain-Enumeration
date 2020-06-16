import os
import subprocess
import argparse
from collections import OrderedDict

"""Argparse for terminal execution"""
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--domain", required=True, help="Target domain to search.")
ap.add_argument("-o", "--output", required=True, help="Output file path to write results into a CSV file.")
ap.add_argument("-k", "--keep", action='store_true', help="Keep files that obtained while the program execution.")
ap.add_argument("-i", "--install", action='store_false', help="Install all modules of Recon-Ng.")
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

    # Install all Recon-Ng modules if install option is given. (Recommended in the first run of the program.
    # Reason: There is no pre-installed modules in the default of Recon-ng)
    if args["install"]:
        subprocess.run(["recon-cli", "-C", "\"marketplace install all\""])
    else:
        pass

    # Optional: Keeping files that returned from tools as an output and created while command execution.
    if args["keep"]:
        pass
    else:
        subprocess.run(["rm", "merged_unique_subdomain_list.txt"])
        subprocess.run(["rm", "theharvester_" + target.split(".")[0] + ".xml"])
        subprocess.run(["rm", "theharvester_" + target.split(".")[0] + "_parsed.txt"])
        subprocess.run(["rm", "sublist3r_" + target.split(".")[0] + ".txt"])
        subprocess.run(["sudo", "rm", "recon-ng_" + target.split(".")[0] + ".txt"])


def sublist3r(target_domain):
    """For Sublist3r Automatization: It scan results for target domain and save them into a file"""
    if os.path.exists('Sublist3r'):
        path = os.path.abspath('Sublist3r')
        sublister = subprocess.run([path + "/./sublist3r.py", "-d", target_domain, "-o", "sublist3r_" +
                                    target_domain.split(".")[0] + ".txt"])
        print(sublister)
    else:
        subprocess.run(["git", "clone", "https://github.com/aboul3la/Sublist3r.git"])
        path = os.path.abspath('Sublist3r')
        sublister = subprocess.run([path + "/./sublist3r.py", "-d", target_domain, "-o", "sublist3r_" +
                                    target_domain.split(".")[0] + ".txt"])
        print(sublister)


def recon_ng(target_domain):
    """For Recon-ng Automatization: It uses two modules of Recon-ng for subdomain scan and save results into a file"""
    # Executing the hackertarget module for the target domain
    subprocess.run(["recon-cli", "-m", "hackertarget", "-c", "options set SOURCE " + target_domain, "-x"])
    # Executing the brute_hosts module for the target domain
    subprocess.run(["recon-cli", "-m", "brute_hosts", "-c", "options set SOURCE " + target_domain, "-x"])
    # Load the reporting module, setting the file name and selecting hosts table from results of recon-ng,
    # then execute the module
    subprocess.run(["sudo", "recon-cli", "-m", "reporting/list", "-c", "options set FILENAME " + os.getcwd() +
                    "/recon-ng_" + target_domain.split(".")[0] + ".txt", "-c" "options set TABLE hosts", "-x"])


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
    return ip_dom_dict


def merge_lists(target_domain):
    """It takes all output files which are obtained from tools and merge them in one file without duplicates"""
    all_lines = ''
    with open("theharvester_" + target_domain.split(".")[0] + "_parsed.txt", "r") as file1:
        for subdomain in file1:
            all_lines += subdomain + "\n"
    with open("recon-ng_" + target_domain.split(".")[0] + ".txt", "r") as file2:
        for subdomain in file2:
            all_lines += subdomain + "\n"
    with open("sublist3r_" + target_domain.split(".")[0] + ".txt", "r") as file3:
        for subdomain in file3:
            all_lines += subdomain + "\n"
    with open("merged_unique_subdomain_list.txt", "w") as wp:
        # Eliminating the duplicate lines.
        unique_list = "\n".join(list(OrderedDict.fromkeys(all_lines.split("\n"))))
        for sub_dom in unique_list.splitlines():
            wp.write("{}\n".format(sub_dom))


def write_csv(result_path):
    """It writes the dictionary returned from ns_lookup() into a csv file with format."""
    dict_to_write = ns_lookup("merged_unique_subdomain_list.txt")
    with open(result_path, "w") as wr:
        for key in dict_to_write:
            wr.write("{},{}\n".format(key, dict_to_write[key]))


if __name__ == '__main__':
    main(args["domain"], args["output"])


