#    Copyright 2018 Fraunhofer IML
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

__author__ = "Dominik Lux"
__credits__ = ["Peter Detzner"]
__maintainer__ = "Dominik Lux"
__version__ = "0.0.1a"
__status__ = "Developement"

TYPE_VALUE_METADATA_NOT_DEFINED_MESSAGE = "One of the following is not defined in json: {type|value|metadata}"
VALUE_EMPTY_MESSAGE = "The Value entered is empty!"


class ReverseEntityAttribute(object):
    """ Here the actual Conversion happens. 
        By initiliazing the class, the _dict is translated into the 
        primitive datatypes. With the variable useMetadata the metadata can be ignored
        It defaults then from:
        Complex, Tuple -> List
        Unicode -> String

    """

    def __init__(self, _dict, useMetadata=True):
        """ throw Error!!
        """
        self.value = None

        if _dict is None:
            raise ValueError(VALUE_EMPTY_MESSAGE)

        if 'type' not in _dict or 'value' not in _dict:
            # Check if a viable struct exists.
            raise ValueError(TYPE_VALUE_METADATA_NOT_DEFINED_MESSAGE)

        if not 'metadata' in _dict:
            useMetadata=False


        if _dict['type'] == '' :
            self.value = _dict['value']

        if _dict['type'] == 'boolean' :
            self.value = bool(_dict['value'])
            return

        if  _dict['type'] == 'number' or _dict['type'] == 'Integer':
            self.value = float(_dict['value'])
            if self.value % 1 == 0.0:
                if useMetadata and 'python' in _dict['metadata']:
                    metadata = _dict['metadata']
                    if metadata['python'] == dict(type="dataType", value="int"):
                        self.value = int(_dict['value'])
                        return
                    else: 
                        self.value = long(_dict['value'])
                        return
                else: 
                    self.value = long(self.value)
                    return
            else:
                return
        

        elif _dict['type'] == 'string':
            # Case String or Unicode
            if useMetadata and 'python' in _dict['metadata']:
                metadata = _dict['metadata']
                if metadata['python'] == dict(type="dataType", value="unicode"):
                    self.value = unicode(_dict['value'])
                    return
            # defaulting to str
            self.value = str(_dict['value'])

        elif _dict['type'] == 'array':
            # Case Complex, Tuple or List
            # First: reverse every element to Obj
            tempList = _dict['value']
            tempValue = list()
            for value in tempList:
                re = ReverseEntityAttribute(value, useMetadata)
                tempValue.append(re.getValue())

            # Second: decide if Complex, Tuple or List
            if useMetadata and 'python' in _dict['metadata']:
                metadata = _dict['metadata']
                if metadata['python'] == dict(type="dataType", value="complex"):
                    self.value = complex(*tempValue)
                    return
                elif metadata['python'] == dict(type="dataType", value="tuple"):
                    self.value = tuple(tempValue)
                    return
            # defaulting to list
            self.value = list(tempValue)

        elif _dict['type'] == 'object':
            # arbitary JSON object with key, value
            tempDict = _dict['value']
            self.value = {}
            for key, value in tempDict.iteritems():
                re = ReverseEntityAttribute(value, useMetadata)
                self.value[key] = re.getValue()
            return

        else:
            # Maybe a class with key, value or another JSON object, check if you can iterate!
            if (not hasattr(_dict['value'], 'iteritems')):
                raise ValueError("Unknown Object-Type: " + _dict['type'] + ". And it is not possible to iterate over this Object-Type!")

            tempDict = {}
            for key, value in _dict['value'].iteritems():
                rea = ReverseEntityAttribute(value, useMetadata)
                tempDict[key] = rea.getValue()
            self.value = tempDict
            return

    def getValue(self):
        return self.value