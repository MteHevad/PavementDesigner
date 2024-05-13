# Explanation

The optimization strategy used by this application follows a 
stochastic approach similar to what a pavement designer may do
manually or with the aid of a spreadsheet.

A manual approach to designing flexible pavement generally follows
these steps:

1. Assume the materials of a flexible pavement section.
2. Adjust section thicknesses until the desired structural number is achieved
3. Repeat this process with different materials
4. Select the lowest cost section.

This automated approach applies the same approach, but the number
of sections trialed is much larger than would be practical by hand.
The approach can be explained as follows:

1. Randomly select 1-4 materials for a section
2. Repeat this until the desired test population is achieved (ie 1000+)
3. Validate each section for basic requirements: 
   1. The section has a surface course on top
   2. Cement and lime-based layers are not in contact
   3. The section does not have multiple subgrade treatments
   4. Layers have a thickness which can be constructed in lifts that fall in a specified range
   5. The section has no duplicate layers
4. Determine the difference between the section structural number and the goal
5. Adjust the thickness of layers, starting with the most cost-effective toward the goal
6. Rank the sections and take the lowest cost section

Because a user can input arbitrary materials, the solver cannot have any
intuition about the appropriateness of any combination of materials. You
are likely to see combinations or ordering of materials
that may be undesirable for practical reasons. There may also be other
reasons why a section may not be appropriate for specific site
conditions. The goal is that by providing multiple solution the
user will have one or more plausible solutions that
meet the design criteria and provide enough information about
construction costs to be useful without requiring the level of resources 
needed for an engineered design.