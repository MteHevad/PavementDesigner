# Materials

This application supports the use of a user supplied list of materials.
Some common paving materials have been supplied as a default to provide
useable examples. The following material data is needed for the solver:

- *Material Name*: A unique identifier for the material
- *Structural Number*: The Structural number per inch of material
- *Minimum Lift*: The smallest practical thickness of a material, such as 3X the aggregate diameter
- *Maximum Lift*: The thickest section which can be compacted to specification
- *Density*: This is needed to convert payables by-weight to a volume
- *Unit Cost*: Price per weight or volume
- *Unit*: Ton, cubic yard, and square yard are the only supported units at this time. Square yards probably should have equal minimum and maximum lifts
- *Surface*: Can this material be used as a surface course?
- *Subgrade Treatment*: Does this material use processed or modified in-situ material?
- *Alkaline*: Does this contain lime or portland cement? Could it bond to another layer?

Excavation costs unclassified, and embankment costs should be the cost of placing fill material. 
The cost should be appropriate if the expectation is that the roadway will be built
by compacting on-site materials or hauled-in materials.