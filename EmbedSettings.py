# -*- encoding: utf-8 -*-

## based on https://github.com/5axes/CuraSettingsWriter
## Embeds the settings tree into the gcode as comments, which allows you to
## figure out what changed between prints when fine tuning things.

import json
import io
import platform
import string

from datetime import datetime

from ..Script import Script

from cura.CuraApplication import CuraApplication
from cura.CuraVersion import CuraVersion

from UM.i18n import i18nCatalog
i18n_cura_catalog = i18nCatalog("cura")
i18n_catalog = i18nCatalog("fdmprinter.def.json")
i18n_extrud_catalog = i18nCatalog("fdmextruder.def.json")


def translate(catalog, context, source):
    return catalog.i18nc(context, source)
    # return source


class EmbedSettings(Script):
    def getSettingDataString(self):
        return json.dumps({
            "name": "Embed Settings",
            "key": "EmbedSettings",
            "metadata": {},
            "version": 2,
            "settings": {
                "enable": {
                    "label": "Enable",
                    "description": "When enabled, will write settings at end of gcode",
                    "type": "bool",
                    "default_value": True
                }
            }
        })

    def execute(self, data):
        if not self.getSettingValueByKey("enable"):
            return data

        stream = io.StringIO()
        stream.write(";START_SETTINGS\n")

        machine_manager = CuraApplication.getInstance().getMachineManager()
        stack = CuraApplication.getInstance().getGlobalContainerStack()

        global_stack = machine_manager.activeMachine

        extruder_count = stack.getProperty("machine_extruder_count", "value")
        extruders = global_stack.extruderList

        print_information = CuraApplication.getInstance().getPrintInformation()

        self._write_kv(stream, translate(i18n_cura_catalog, "@label", "Job Name"), print_information.jobName)
        self._write_kv(stream, "Date", datetime.now().isoformat())
        self._write_kv(stream, "Os", "{} {}".format(platform.system(), platform.version()))
        self._write_kv(stream, "Cura Version", CuraVersion)

        self._write_kv(stream, translate(i18n_cura_catalog, "@label", "Profile"), global_stack.qualityChanges.getMetaData().get("name", ""))
        self._write_kv(stream, translate(i18n_cura_catalog, "@label:table_header", "Quality"), global_stack.quality.getMetaData().get("name", ""))

        # Material
        for i, extruder in enumerate(extruders):
            M_Name = extruder.material.getMetaData().get("material", "")
            MaterialStr = "%s %s : %d" % (translate(i18n_cura_catalog, "@label", "Material"), translate(i18n_cura_catalog, "@label", "Extruder"), i)
            self._write_kv(stream, MaterialStr, M_Name)

        material_weight = sum(print_information.materialWeights, 0)
        if material_weight > 0:
            self._write_kv(stream, translate(i18n_cura_catalog, "@label", "Material estimation"), "{:.1f}g".format(material_weight))

        self._write_kv(stream, translate(i18n_cura_catalog, "@label", "Printing Time"), print_information.currentPrintTime.getDisplayString())

        # Define every section to get the same order as in the Cura Interface
        # Modification from global_stack to extruders[0]
        for i, extruder in enumerate(extruders):
            self._doTree(extruder, "resolution", stream, 0, i)
            self._doTree(extruder, "shell",      stream, 0, i)
            self._doTree(extruder, "infill",     stream, 0, i)
            self._doTree(extruder, "material",   stream, 0, i)
            self._doTree(extruder, "speed",      stream, 0, i)
            self._doTree(extruder, "travel",     stream, 0, i)
            self._doTree(extruder, "cooling",    stream, 0, i)

            # If single extruder doesn't export the data
            if extruder_count>1 :
                self._doTree(extruder, "dual", stream, 0, i)

        self._doTree(extruders[0],"support", stream, 0, 0)
        self._doTree(extruders[0],"platform_adhesion", stream, 0, 0)

        for i, extruder in enumerate(extruders):
            self._doTree(extruder, "meshfix", stream, 0, i)

        self._doTree(extruders[0], "blackmagic", stream, 0, 0)
        self._doTree(extruders[0], "experimental", stream, 0, 0)
        self._doTree(extruders[0], "machine_settings", stream, 0, 0)

        for i, extruder in enumerate(extruders):
            self._doTreeExtrud(extruder, "machine_settings", stream, 0, i)

        # set_trace(port=4444)

        stream.write(";END_SETTINGS\n")

        ## some characters, like 40°C and 800mm/s² aren't ascii-encodable and cause errors
        data.append("".join(filter(lambda x: x in string.printable, stream.getvalue())))

        return data

    def _write_kv(self, stream, key, val, depth=0):
        stream.write("; {}{} = {}\n".format(" " * depth * 4, key, val.replace('\n', '\\n')))

    def _doTree(self, stack, key, stream, depth, extrud):
        untranslated_label = stack.getProperty(key, "label")
        translated_label = translate(i18n_catalog, key + " label", untranslated_label)

        if stack.getProperty(key, "type") == "category":
            Info_Extrud = translated_label

            if extrud > 0:
                Info_Extrud = "{}: {} {}".format(
                    translate(i18n_cura_catalog, "@label", "Extruder"),
                    extrud,
                    translated_label,
                )

            stream.write("; {}>> {} <<\n".format(" " * depth * 4, Info_Extrud))
        else:
            disabled = stack.getProperty(key,"enabled") is False

            val = "{}{}".format(stack.getProperty(key, "value"), stack.getProperty(key, "unit"))
            if disabled:
                val += " (disabled)"

            self._write_kv(stream, translated_label, val, depth=depth)

            depth += 1

        for i in CuraApplication.getInstance().getGlobalContainerStack().getSettingDefinition(key).children:
            self._doTree(stack, i.key, stream, depth, extrud)

    def _doTreeExtrud(self, stack, key, stream, depth, extrud):
        untranslated_label = stack.getProperty(key, "label")
        translated_label = translate(i18n_extrud_catalog, key + " label", untranslated_label)

        if stack.getProperty(key,"type") == "category":
            Info_Extrud = translated_label

            if extrud > 0:
                Info_Extrud = "{}: {} {}".format(
                    translate(i18n_cura_catalog, "@label", "Extruder"),
                    extrud,
                    translated_label,
                )

            stream.write("; {}>> {} <<\n".format(" " * depth * 4, Info_Extrud))
        else:
            disabled = stack.getProperty(key,"enabled") is False

            val = "{}{}".format(stack.getProperty(key, "value"), stack.getProperty(key, "unit"))
            if disabled:
                val += " (disabled)"

            self._write_kv(stream, translated_label, val, depth=depth)

            depth += 1

        for i in stack.getSettingDefinition(key).children:
            self._doTreeExtrud(stack, i.key, stream, depth, extrud)
