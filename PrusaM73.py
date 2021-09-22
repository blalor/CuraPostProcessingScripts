# -*- encoding: utf-8 -*-

## https://reprap.org/wiki/G-code#M73:_Set.2FGet_build_percentage

import json
from ..Script import Script


class PrusaM73(Script):
    def getSettingDataString(self):
        return json.dumps({
            "name": "Prusa M73",
            "key": "PrusaM73",
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

    def execute(self, layers):
        ## make no changes if we're not enabled
        if not self.getSettingValueByKey("enable"):
            return layers

        ## unset until we find the time in the source data
        total_time = None

        ## walk over each layer
        for layer_ind, layer_data in enumerate(layers):
            ## split layer data into lines
            layer_instructions = layer_data.split("\n")
            new_layer_instructions = []

            for li in layer_instructions:
                ## always capture the original layer info
                new_layer_instructions.append(li)

                ## capture the total print time
                if total_time is None and li.startswith(";TIME:"):
                    total_time = float(li.split(":", 2)[1])

                ## capture the elapsed time, and if the total_time has been
                ## found, emit the M73 instruction.
                if total_time is not None:
                    if li.startswith(";LAYER:0"):
                        time_remaining = round(total_time / 60.0)
                        new_layer_instructions.append("M73 P0 R{}".format(time_remaining))
                        
                    elif li.startswith(";TIME_ELAPSED:"):
                        elapsed_time = float(li.split(":", 2)[1])

                        progress_pct = round(elapsed_time * 100.0 / total_time)
                        time_remaining = round((total_time - elapsed_time) / 60.0)

                        new_layer_instructions.append("M73 P{} R{}".format(progress_pct, time_remaining))

            ## replace the layer instructions with our new augmented ones
            layers[layer_ind] = "\n".join(new_layer_instructions)

        return layers
