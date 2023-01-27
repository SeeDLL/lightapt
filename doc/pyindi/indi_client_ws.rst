IndiClientWS api
=====================

architecture
---------------

this api will accept instruction and parameters through websocket message, and call corresponding function.

all functions are designed to operate one indi device and properties, through pyindi_client interface,
and return result through websocket api in json or binary data.

client(send instruction) -> websocket api -> pyindi_client (got data or response) -> websocket api -> client

return data struct
-------------------------

return data can have two types, json data or binary.

json data
++++++++++++++

json data struct will be::

    'type': str,  indicate which type of message is
    'message': str, if the type is message or error, this keyword will have information
    'data': None or dict, if type is 'data' this will have a dict for information.

type will have those categories:

* message: if type is message, see message information, it will contain normal return of instruction execution result.
if there is some error can be handled automatically, the message will prefixed by 'ERROR!'.
if the instruction do not have any response, as it just handle switches or numbers of indi device, then message
will only contain 'success'.
* data: if type is data, the 'data' keyword will have a dict contains all data
* error: if type is error, see 'message', it normally indicated there is an program error which is not probably handled.
* signal: if this is a signal for instruction finish, the websocket will send extra task finish signal.

binary
++++++++++++++

binary data will only send picture data.

detailed binary transmission need to be determined later.

websocket api usage
---------------------------

websocket api is designed to be used in three methods:

* get information of devices.
* set parameters of devices.
* call devices to carry out some instructions.

for each method

get information
+++++++++++++++++++++

normally, these types of methods will get `data` in websocket response. The response will be
returned immediately as it do not do any changes to any devices.

set parameters of devices
++++++++++++++++++++++++++++++

usually, set parameters will get `message` response and get `success` in `message` keyword.
set parameter only changes numbers, switches of indi device instance, and should be returned
immediately after this is called.

call device to carry out instruction
+++++++++++++++++++++++++++++++++++++++++

this type of method in general are done by changing numbers, switches of indi devices, the same as
set parameters of devices.
However, these methods will let devices to do some work in real world, such as telescope goto, camera take exposure.
Usually, those work in real world will not be finished immediately, and need to be waited afterwords.
This can also be called asynchronous interrupt.
So the response in those instruction will be:
1, return a `message` with `success` as the devices.
2, will return a end of instruction signal, with `signal` in `type` keyword, and other information in `message`
    or `data` keyword. if there is no data, data will be empty.

class data structure
============================

device instance basic requirement
------------------------------------

connection and disconnection
+++++++++++++++++++++++++++++++++

for the time being, connecting devices are the same, use the base device class method.

check parameters
+++++++++++++++++++

as each different type of devices has different switch numbers for some specific controls. Therefore,
each device need to check whether they can do such control after its connections.

As different device have different checks. This function must be written for each device class.

all methods
++++++++++++++++++

all instructions should be written as async, `async` must be added before each device class instruction
function.

more detailed requirements will be described later.

methods with asynchronous interrupt, should handle the asynchronous steps by function it self.

device methods function call template
------------------------------------------------

this is the detailed description of all methods function and parameters definition.

function parameters
++++++++++++++++++++++

for example, an complex method function definition will be::

    async def method_function(self, param1, param2, *args, **kwargs)

part 1 method bound parameters.

each method or instruction to device, if have parameters, which are transmitted by
websocket api, will be transmitted to function directly by unpacking those parameters into position
parameters.

for example, if the method must have one parameter, but may have one or two options parameters.

in most cases, the parameter will be send by websocket by [param1]

if it need one options parameter, then websocket will send [param1, param2]

in function definition, as param1 is mandatory, but param2 and param3 are optional. So the function definition
will be::

    async def method_function(self, param1, *args, **kwargs)

as data sent by websocket will be unpacked by *args, therefore, each param1 will send directly. param2 and
param3 will be unpacked in *args in case they exist.

* in sending parameters through websocket api, the sequence of parameters are very important. *

part 2 environment bound parameters.

These parameters are not related to method or websocket data directly. It is bounded to connected devices,
running environment and sequence process.

Therefore, all the data are send through kwargs, keyword argument.

For the time bing, defined keywords are::

    ws_instance: this websocket connection instance. can be called with .write() to send message.
    target_info: sequance target information
    exposure_time: as name
    ccd1:  main camera CCD1 blob
    count: subframe count number, in int
    filter_info: filter information, in progress
    phd2_object: phd2 object, in progress

So, if the asynchronous interrupt need such information to send response, do other things, can find data in
kargs.
Especially for sending response, it will definite use ws_instance to write data. this keyword is
initialed in py_indi_websocket, so each function can see this keyword.
However, other keywords are initialed by its own function, therefore each keyword must be checked before
usage, and ensure it is correctly initialed.
