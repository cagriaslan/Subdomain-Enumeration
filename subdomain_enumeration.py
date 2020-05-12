import os
import sys
import subprocess


def auto_recon(target_domain):
    """For theHarvester: The file 'api-keys.yaml' must exist under the directory where the command executed"""

    harvester = subprocess.run(["theHarvester", "-d", target_domain, "-b", "all", "-f", "output.xml"], check=True)
    print(harvester)

    if os.path.exists('Sublist3r'):
        path = os.path.abspath('Sublist3r')
        sublister = subprocess.run([path + "./sublist3r.py", "-d", target_domain, "-o", "sublist3r" + target_domain.split(".")[0] + ".txt"])
        print(sublister)
    else:
        subprocess.run(["git", "clone", "https://github.com/aboul3la/Sublist3r.git"])
        path = os.path.abspath('Sublist3r')
        sublister = subprocess.run([path + "./sublist3r.py", "-d", target_domain, "-o", "sublist3r" + target_domain.split(".")[0] + ".txt"])
        print(sublister)

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
    subprocess.run(["recon-cli", "-m", "reporting/list", "-c", "\"options set FILENAME recon-ng.txt\"", "-c" "options set TABLE hosts", "-x"])


def ns_lookup(subdomain_list):
    ip_dom_dict = {}
    with open(subdomain_list, "r") as file:
        for subdomain in file:
            try:
                process = subprocess.run(["nslookup", subdomain.split("\n", 1)[0]], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output = process.stdout
                for idx, row in enumerate(output.splitlines()):
                    if idx == 4:
                        dom_name = row.split(":")[1]
                    if idx == 5:
                        ip_add = row.split(":")[1]
                        ip_dom_dict[dom_name.split("\t")[1]] = ip_add.split()[0]
            except:
                print("An error occured for " + subdomain.split("\n", 1)[0])

    print(ip_dom_dict)


ns_lookup("reconng.txt")
