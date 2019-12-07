# Justin113D's Blender tools for 2.81
_A set of tools i put together from time to time to make life in blender easier_


## Installation
1. Download the repository as a .zip (green "**clone or download**" button)
2. In Blender, open the preferences and got to the addons tab
3. Click "Install" on the top left and select the downloaded zip file. 
   - **Don't extract the zip's contents!** The zip has to be used as is!
4. The addon should be installed! Have fun!

## Features
### General
##### Copy and Paste selected Modifiers and Constraints
A thing that was always missing from blender was to copy and paste specific modifiers or constraints, without deleting existing ones on the target object.
I got tired of it too, and decided to add the functionality in myself! 

To **copy** specific Modifiers/Constraints, simply collapse the constraints that you dont want to copy. Then hit **Ctrl + C**!  <br>
The cursor needs to be inside the corresponding menu, above some empty space. If all space is blocked, its easiest to just hover above one of the modifier's/constraints icons when copying.

To **paste** them, press **Ctrl + V** into the menu! <br>
Here the same rules for the cursor apply as for copying.

### Weights
#### Weightpainting
##### Average weights
Location: `Weights -> Average weight` <br>
To use this operator, you need to be in either **paint mask mode** (faces or vertices). <br>
When used, it will take the weights of all selected vertices of the current active group, average them, and replace the weights with it

#### Vertex groups
##### Remove Empty
Location: `Properties -> Mesh -> Vertex Groups -> 🆅 -> Remove Empty` <br>
Removes all groups that dont hold any weights

##### Remove Unused
Location: `Properties -> Mesh -> Vertex Groups -> 🆅 -> Remove Unused` <br> 
Removes all groups which are not used by the armature (WIP)
