# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re
import os
import sys

_COMMON_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(1, _COMMON_PATH)
from dcid_existance import check_dcid_existance


def _generate_mcf(sv_list, mcf_file_path) -> None:
    """
    This method generates MCF file w.r.t
    dataframe headers and defined MCF template.

    Args:
        sv_list (list) : List of DataFrame Columns

    Returns:
        None
    """
    # pylint: disable=R0914
    # pylint: disable=R0912
    # pylint: disable=R0915
    actual_mcf_template = ("Node: dcid:{}\n"
                           "name: \"{}\"\n"
                           "typeOf: dcs:StatisticalVariable\n"
                           "populationType: dcs:Person{}{}{}{}{}{}{}{}{}{}{}\n"
                           "statType: dcs:measuredValue\n"
                           "measuredProperty: dcs:count\n")
    final_mcf_template = ""
    for sv in sv_list:
        if "Total" in sv:
            continue
        incomequin = ''
        gender = ''
        education = ''
        healthbehavior = ''
        exercise = ''
        residence = ''
        activity = ''
        duration = ''
        countryofbirth = ''
        citizenship = ''
        lev_limit = ''
        sv_name = ''

        sv_prop = sv.split("_")

        for prop in sv_prop:
            if prop in ["Count"]:
                continue
            elif prop in ["Person"]:
                sv_name = sv_name + "Population: "
            if "PhysicalActivity" in prop:
                healthbehavior = "\nhealthBehavior: dcs:" + prop
                sv_name = sv_name + prop + ", "
            elif "Male" in prop or "Female" in prop:
                gender = "\ngender: dcs:" + prop
                sv_name = sv_name + prop + ", "
            elif "Aerobic" in prop or "MuscleStrengthening" in prop \
                or "Walking" in prop or "Cycling" in prop:
                exercise = "\nexerciseType: dcs:" + prop
                sv_name = sv_name + prop + ", "
            elif "Education" in prop:
                education = "\neducationalAttainment: dcs:" + \
                    prop.replace("EducationalAttainment","")\
                    .replace("Or","__")
                sv_name = sv_name + prop + ", "
            elif "Percentile" in prop:
                incomequin = "\nincome: ["+prop.replace("Percentile",\
                    "").replace("To"," ").replace("IncomeOf","")+" Percentile]"
                sv_name = sv_name + prop + ", "
            elif "Urban" in prop or "SemiUrban" in prop \
                or "Rural" in prop:
                residence = "\nplaceOfResidenceClassification: dcs:" + prop
                sv_name = sv_name + prop + ", "
            elif "Activity" in prop:
                activity = "\nphysicalActivityEffortLevel: dcs:" + prop
                sv_name = sv_name + prop + ", "
            elif "Minutes" in prop:
                sv_name = sv_name + prop + ", "
                if "OrMoreMinutes" in prop:
                    duration = "\nduration: [" + prop.replace\
                        ("OrMoreMinutes","") + " - Minutes]"
                elif "To" in prop:
                    duration = "\nduration: [" + prop.replace("Minutes",\
                            "").replace("To", " ") + " Minutes]"
                else:
                    duration = "\nduration: [Minutes " + prop.replace\
                        ("Minutes","") + "]"
            elif "ForeignBorn" in prop or "Native" in prop:
                countryofbirth = "\nnativity: dcs:" + \
                    prop.replace("CountryOfBirth","")
                sv_name = sv_name + prop + ", "
            elif "ForeignWithin" in prop or "ForeignOutside" in prop\
                or "Citizen" in prop:
                citizenship = "\ncitizenship: dcs:" + \
                    prop.replace("Citizenship","")
                sv_name = sv_name + prop + ", "
            elif "Moderate" in prop or "Severe" in prop \
                or "None" in prop:
                lev_limit = "\nglobalActivityLimitationindicator: dcs:"\
                    + prop
                sv_name = sv_name + prop + ", "
            elif "weight" in prop or "Normal" in prop \
                or "Obese" in prop or "Obesity" in prop:
                healthbehavior = "\nhealthBehavior: dcs:" + prop
                sv_name = sv_name + prop + ", "
        sv_name = sv_name.rstrip(', ')
        sv_name = re.sub(r"(\w)([A-Z])", r"\1 \2", sv_name)
        sv_name = sv_name.replace("To", "To ").replace("Of", "Of ").replace(
            "ACitizen", "A Citizen")
        final_mcf_template += actual_mcf_template.format(
            sv, sv_name, incomequin, education, healthbehavior, exercise,
            residence, activity, duration, gender, countryofbirth, citizenship,
            lev_limit) + "\n"

    # Writing Genereated MCF to local path.
    with open(mcf_file_path, 'w+', encoding='utf-8') as f_out:
        f_out.write(final_mcf_template.rstrip('\n'))


_MODULE_DIR = "scripts/eurostat/health_determinants/fruits_vegetables/"

_INPUT_MCF_FILE_PATH = os.path.join(
    _MODULE_DIR, "output",
    "eurostat_population_consumptionoffruitsandvegetables.mcf")
_OUTPUT_MCF_FILE_PATH = os.path.join(
    _MODULE_DIR, "output",
    "eurostat_population_consumptionoffruitsandvegetables_deno.mcf")

with open(_INPUT_MCF_FILE_PATH, "r") as mcf_file:
    mcf = mcf_file.read()
    deno_matched = re.findall(r"(measurementDenominator: dcs:)(\w+)", mcf)
    f_deno = []
    for deno in deno_matched:
        f_deno.append(deno[1])
    f_deno = list(set(f_deno))
    node_status = check_dcid_existance(f_deno)
    f_deno = []
    for node, status in node_status.items():
        if not status:
            f_deno.append(node)
    f_deno.sort()
    _generate_mcf(f_deno, _OUTPUT_MCF_FILE_PATH)