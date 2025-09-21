#!env python3

# Twister Puzzle Solver
#
# In this game, 27 cubes are stringed together so that they can only twist
# in certain ways. The goal is to arrange the cubes to form a 3x3x3 large
# cube.
#
# Each cube has 6 faces. We number the faces 0 to 5 such that opposite faces
# have the same number modulo 3. For example, faces 0 and 3 are opposite,
# faces 1 and 4 are opposite, and faces 2 and 5 are opposite. This means that
# for each face i, face j is adjoining iff j != i mod 3.
#
# The cubes are stringed together in a twisted chain. Except for the two
# end cubes, each cube is connected to two other cubes. Each connection
# connects two adjoining faces of the two cubes. The two end cubes are each
# connected to only one other cube.
#
# Two connected cubes can be twisted relative to each other. A twist
# operation rotates the two cubes around the axis formed by the two
# connected faces. A twist operation rotates one cube by 90 degrees.
# A twist doesn't change which faces are connected, but it does change
# the orientation of the two cubes relative to each other.
#
# Each cube has an ID number from 0 to 26. Cube i is connected to cube
# i-1 and cube i+1, except for cube 0 which is connected to cube 1,
# and cube 26 which is connected to cube 25.
#
# The state of a cube consists of the cube's location in the 3D space
# and the cube's orientation. The location is represented by a 3D vector
# (x,y,z). The orientation is represented by a permutation of the numbers
# 0 to 5, where the 0-th element is the face that points in the -x direction,
# the 1-st element is the face that points in the +x direction, the 2-nd
# element is the face that points in the -y direction, the 3-rd element is
# the face that points in the +y direction, the 4-th element is the face
# that points in the -z direction, and the 5-th element is the face that
# points in the +z direction.
#
# We represent the connection between two cubes by a tuple (i,j) where i is the
# face of the first cube and j is the face of the second cube that are connected.

from typing import Optional



class Location:
    """Represents a location in 3D space."""

    def __init__(self, x: int, y: int, z: int) -> None:
        """Initialize the location."""
        self._coords = (x, y, z)

    @property
    def x(self) -> int:
        """The x coordinate of the location."""
        return self._coords[0]

    @property
    def y(self) -> int:
        """The y coordinate of the location."""
        return self._coords[1]

    @property
    def z(self) -> int:
        """The z coordinate of the location."""
        return self._coords[2]

    def __add__(self, other: "Direction") -> "Location":
        """Add a direction vector to this location."""
        return Location(
            self._coords[0] + other.x,
            self._coords[1] + other.y,
            self._coords[2] + other.z,
        )

    def __sub__(self, other: "Location") -> "Direction":
        """Subtract another location from this location to get a direction vector."""
        return Direction(
            self._coords[0] - other.x,
            self._coords[1] - other.y,
            self._coords[2] - other.z,
        )

    def __eq__(self, other: object) -> bool:
        """Check if two locations are equal."""
        if not isinstance(other, Location):
            return NotImplemented
        return self._coords == other._coords

    def in_bounds(self) -> bool:
        """Check if the location is within the 3x3x3 grid."""
        return all(0 <= coord < 3 for coord in self._coords)

    def __str__(self) -> str:
        return f"({self._coords[0]}, {self._coords[1]}, {self._coords[2]})"


class Face:
    """Represents a face of a cube."""

    def __init__(self, index: int) -> None:
        """Initialize the face with its index."""
        assert 0 <= index < 6
        self._index = index

    @property
    def index(self) -> int:
        """The index of the face."""
        return self._index

    def opposite(self) -> "Face":
        """Return the opposite face."""
        return Face((self._index + 3) % 6)

    def is_opposite(self, other: "Face") -> bool:
        """Check if this face is opposite to another face."""
        return (self._index + 3) % 6 == other.index

    def is_adjoining(self, other: "Face") -> bool:
        """Check if this face is adjoining to another face."""
        return self._index % 3 != other.index % 3

    def __eq__(self, other: object) -> bool:
        """Check if two faces are equal."""
        if not isinstance(other, Face):
            return NotImplemented
        return self._index == other.index

    def __str__(self) -> str:
        return f"Face{self._index}"


class Direction:
    """Represents a direction vector in 3D space."""

    def __init__(self, x: int, y: int, z: int) -> None:
        """Initialize the direction vector."""
        assert (x, y, z) in {
            (-1, 0, 0),
            (1, 0, 0),
            (0, -1, 0),
            (0, 1, 0),
            (0, 0, -1),
            (0, 0, 1),
        }
        self._vector = (x, y, z)

    @property
    def x(self) -> int:
        """The x component of the direction vector."""
        return self._vector[0]

    @property
    def y(self) -> int:
        """The y component of the direction vector."""
        return self._vector[1]

    @property
    def z(self) -> int:
        """The z component of the direction vector."""
        return self._vector[2]

    def reverse(self) -> "Direction":
        """Return the opposite direction."""
        return Direction(-self._vector[0], -self._vector[1], -self._vector[2])

    def __eq__(self, other: object) -> bool:
        """Check if two directions are equal."""
        if not isinstance(other, Direction):
            return NotImplemented
        return self._vector == other._vector

    def __str__(self) -> str:
        if self.x == -1:
            return "-X"
        elif self.x == 1:
            return "+X"
        elif self.y == -1:
            return "-Y"
        elif self.y == 1:
            return "+Y"
        elif self.z == -1:
            return "-Z"
        elif self.z == 1:
            return "+Z"
        raise ValueError("Invalid direction")


class Orientation:
    """Represents a cube orientation."""

    def __init__(self, neg_x_face: Face, neg_y_face: Face, neg_z_face: Face) -> None:
        """Initialize the orientation given the faces pointing in the -x, -y, -z directions."""
        assert neg_x_face.is_adjoining(neg_y_face)
        assert neg_x_face.is_adjoining(neg_z_face)
        assert neg_y_face.is_adjoining(neg_z_face)
        self._neg_faces = (neg_x_face, neg_y_face, neg_z_face)

    @property
    def x_face(self) -> Face:
        """The face pointing in the +x direction."""
        return self.neg_x_face.opposite()

    @property
    def y_face(self) -> Face:
        """The face pointing in the +y direction."""
        return self.neg_y_face.opposite()

    @property
    def z_face(self) -> Face:
        """The face pointing in the +z direction."""
        return self.neg_z_face.opposite()

    @property
    def neg_x_face(self) -> Face:
        """The face pointing in the -x direction."""
        return self._neg_faces[0]

    @property
    def neg_y_face(self) -> Face:
        """The face pointing in the -y direction."""
        return self._neg_faces[1]

    @property
    def neg_z_face(self) -> Face:
        """The face pointing in the -z direction."""
        return self._neg_faces[2]

    def face_direction(self, face: Face) -> Direction:
        """Get the direction vector of a face of this cube."""
        if face == self.neg_x_face:
            return Direction(-1, 0, 0)
        elif face == self.x_face:
            return Direction(1, 0, 0)
        elif face == self.neg_y_face:
            return Direction(0, -1, 0)
        elif face == self.y_face:
            return Direction(0, 1, 0)
        elif face == self.neg_z_face:
            return Direction(0, 0, -1)
        elif face == self.z_face:
            return Direction(0, 0, 1)
        else:
            raise ValueError(f"Invalid face: {face}")

    def right_hand_rotate(self, axis_face: Face) -> "Orientation":
        """Return a new orientation obtained by rotating this orientation 90 degrees
        clockwise around the axis defined by the given face."""
        if axis_face == self.neg_x_face or axis_face == self.x_face:
            # Rotate around x-axis: y -> z -> -y -> -z -> y
            return Orientation(
                self.neg_x_face,
                self.neg_z_face,
                self.y_face,
            )
        elif axis_face == self.neg_y_face or axis_face == self.y_face:
            # Rotate around y-axis: z -> x -> -z -> -x -> z
            return Orientation(
                self.z_face,
                self.neg_y_face,
                self.neg_x_face,
            )
        elif axis_face == self.neg_z_face or axis_face == self.z_face:
            # Rotate around z-axis: x -> y -> -x -> -y -> x
            return Orientation(
                self.neg_y_face,
                self.x_face,
                self.neg_z_face,
            )
        else:
            raise ValueError(f"Invalid axis face: {axis_face}")

    def __eq__(self, value: object) -> bool:
        """Check if two orientations are equal."""
        if not isinstance(value, Orientation):
            return NotImplemented
        return self._neg_faces == value._neg_faces

    def __str__(self) -> str:
        return f"Orientation(neg_x={self.neg_x_face}, neg_y={self.neg_y_face}, neg_z={self.neg_z_face})"

# This list of 27 elements represents the connections between the 27 cubes.
# The i-th element is a tuple (a,b) where a is the face of cube i that is
# connected to cube i-1, and b is the face of cube i that is connected to
# cube i+1. For cube 0, a is None. For cube 26, b is None.
FACES_TO_NEIGHBORS: list[tuple[Optional[Face], Optional[Face]]] = [
    (None, Face(3)),  # Cube 0 is connected to cube 1 via face 3
    (Face(0), Face(3)),  # Cube 1 is connected to cube 0 via face 0 and cube 2 via face 3
    (Face(0), Face(1)),  # Cube 2 is connected to cube 1 via face 0 and cube 3 via face 1
    (Face(0), Face(3)),  # Cube 3 is connected to cube 2 via face 0 and cube 4 via face 3
    (Face(0), Face(1)),  # Cube 4 is connected to cube 3 via face 0 and cube 5 via face 1
    (Face(0), Face(3)),  # Cube 5 is connected to cube 4 via face 0 and cube 6 via face 3
    (Face(0), Face(1)),  # Cube 6 is connected to cube 5 via face 0 and cube 7 via face 1
    (Face(0), Face(3)),  # Cube 7 is connected to cube 6 via face 2 and cube 8 via face 1
    (Face(0), Face(1)),  # Cube 8 is connected to cube 7 via face 2 and cube 9 via face 1
    (Face(0), Face(1)),  # Cube 9 is connected to cube 8 via face 2 and cube10 via face1
    (Face(0), Face(1)),  # Cube10 is connected to cube 9 via face 2 and cube11 via face5
    (Face(0), Face(1)),  # Cube11 is connected to cube10 via face 4 and cube12 via face5
    (Face(0), Face(3)),  # Cube12 is connected to cube11 via face 4 and cube13 via face5
    (Face(0), Face(1)),  # Cube13 is connected to cube12 via face 4 and cube14 via face5
    (Face(0), Face(3)),  # Cube14 is connected to cube13 via face 4 and cube15 via face5
    (Face(0), Face(1)),  # Cube15 is connected to cube14 via face 4 and cube16 via face1
    (Face(0), Face(1)),  # Cube16 is connected to cube15 via face 2 and cube17 via face1
    (Face(0), Face(1)),  # Cube17 is connected to cube16 via face 2 and cube18 via face1
    (Face(0), Face(3)),  # Cube18 is connected to cube17 via face 2 and cube19 via face1
    (Face(0), Face(1)),  # Cube19 is connected to cube18 via face 2 and cube20 via face1
    (Face(0), Face(1)),  # Cube20 is connected to cube19 via face 2 and cube21 via face3
    (Face(0), Face(3)),  # Cube21 is connected to cube20 via face 0 and cube22 via face3
    (Face(0), Face(1)),  # Cube22 is connected to cube21 via face 0 and cube23 via face3
    (Face(0), Face(1)),  # Cube23 is connected to cube22 via face 0 and cube24 via face3
    (Face(0), Face(1)),  # Cube24 is connected to cube23 via face 0 and cube25 via face3
    (Face(0), Face(3)),  # Cube25 is connected to cube24 via face 0 and cube26 via face3
    (Face(0), None),  # Cube25 is connected to cube24 via face 0
]


# The locations of the cubes that have been placed in the 3x3x3 grid so far.
LOCATIONS: list[Location] = []

# The orientations of the cubes that have been placed in the 3x3x3 grid so far.
ORIENTATIONS: list[Orientation] = []


def face0_towards(direction: Direction) -> Orientation:
    """Return an orientation where face 0 points towards the given direction.
    
    The other two faces (neg_y and neg_z) can be chosen arbitrarily.
    """
    if direction == Direction(-1, 0, 0):
        return Orientation(Face(0), Face(1), Face(2))
    elif direction == Direction(1, 0, 0):
        return Orientation(Face(3), Face(5), Face(4))
    elif direction == Direction(0, -1, 0):
        return Orientation(Face(2), Face(0), Face(1))
    elif direction == Direction(0, 1, 0):
        return Orientation(Face(4), Face(3), Face(5))
    elif direction == Direction(0, 0, -1):
        return Orientation(Face(1), Face(2), Face(0))
    elif direction == Direction(0, 0, 1):
        return Orientation(Face(5), Face(4), Face(3))
    else:
        raise ValueError(f"Invalid direction: {direction}")

def reverse_order(locs: list[Location]) -> list[Location]:
    """Return a new list with the locations in reverse order."""
    return list(reversed(locs))

def mirror_xyz(locs: list[Location]) -> list[Location]:
    """Return a new list with the locations mirrored along the x, y, and z axes."""
    return [Location(2 - loc.x, 2 - loc.y, 2 - loc.z) for loc in locs]

def dfs(cube_index: int):
    """Depth-first search to place cube `cube_index` in the grid."""

    assert 0 < cube_index <= 27
    if cube_index == 27:
        print("Found a solution!")
        for i, loc in enumerate(LOCATIONS):
            print(f"Cube {i:2d}: {loc}")
            if i + 1 >= len(LOCATIONS):
                continue
            next_loc = LOCATIONS[i + 1]
            print("          ", end="")
            print("|" if loc.x != next_loc.x else " ", end="")
            print("  ", end="")
            print("|" if loc.y != next_loc.y else " ", end="")
            print("  ", end="")
            print("|" if loc.z != next_loc.z else " ")

        # It's easier to move the cubes in the reverse order.
        locs = mirror_xyz(reverse_order(LOCATIONS))
        for i, loc in enumerate(locs[:-1]):
            next_loc = locs[i + 1]
            level = ".." if loc.z == 0 else "--" if loc.z == 1 else "=="
            if next_loc.x > loc.x:
                print(f"{level}> ", end="")
            elif next_loc.x < loc.x:
                print(f"<{level} ", end="")
            elif next_loc.y > loc.y:
                print(f"{level}^ ", end="")
            elif next_loc.y < loc.y:
                print(f"{level}v ", end="")
            elif next_loc.z > loc.z:
                print(f"(.) ", end="")
            else:
                print(f"(*) ", end="")
            if i % 5 == 4:
                print()
        print()

        print("""
------------------

              


              
  <2> - (v)
------------------
        (1) > (1)
         |     |
        (1)   (1)
         |     |
        <1>   (^)
-----------------
              

  (v) - (2) - (2)
               |
              <2>
-----------------
  (^) - (0) - (0)        
               |
  <0> - (0)   (0)
         |     |
        (0) - (0)
-----------------
  <2> - (2) - (2)

              """)

        return True

    # Get the connection faces for the current cube.
    face_to_prev, face_to_next = FACES_TO_NEIGHBORS[cube_index]
    assert face_to_prev == Face(0)  # We always connect to the previous cube via face 0.
    # TODO: don't store face_to_prev in FACES_TO_NEIGHBORS, since it's always face 0.

    # Get the location and orientation of the previous cube.
    prev_location = LOCATIONS[cube_index - 1]
    prev_orientation = ORIENTATIONS[cube_index - 1]

    # The face of the previous cube that connects to the current cube.
    prev_face_to_curr = FACES_TO_NEIGHBORS[cube_index - 1][1]
    assert prev_face_to_curr is not None

    # Determine the location of the current cube based on the previous cube's location,
    # orientation, and the face connecting to this cube.

    # The direction vector from the previous cube to the current cube.
    direction = prev_orientation.face_direction(prev_face_to_curr)
    # The location of this cube.
    curr_location = prev_location + direction
    if not curr_location.in_bounds():
        return False
    if curr_location in LOCATIONS:
        return False

    # Try all possible orientations for the current cube. The constraint is that
    # the face connecting to the previous cube must be in the opposite direction
    # of the face connecting to this cube.
    reverse_direction = direction.reverse()
    # face_to_prev must point in reverse_direction. This leaves 4 possible orientations
    # for the current cube. Furthermore, when face_to_prev and face_to_next are opposite,
    # there's no point turning the current cube, so we only need to consider 1 orientation
    # in that case.
    orientation = face0_towards(reverse_direction)
    orientations = [orientation]
    if face_to_next is not None and not face_to_prev.is_opposite(face_to_next):
        for _ in range(3):
            orientation = orientation.right_hand_rotate(face_to_prev)
            orientations.append(orientation)
    # Place the current cube in the grid.
    LOCATIONS.append(curr_location)
    for curr_orientation in orientations:
        ORIENTATIONS.append(curr_orientation)
        # Recursively place the next cube.
        if dfs(cube_index + 1):
            return True
        # Backtrack: rotate the current cube.
        ORIENTATIONS.pop()
    # Backtrack: remove the current cube from the grid.
    LOCATIONS.pop()


def main():
    print("Welcome to Twister!")

    # First, place cube 0 in the grid. Because the first 3 cubes are in a line,
    # without loss of generality, we can place them along the x-axis with cube
    # 0 at (x=0,y,z), where 0 <= y <= 1 and 0 <= z <= 1.
    for y in range(2):
        for z in range(2):
            assert len(LOCATIONS) == 0
            assert len(ORIENTATIONS) == 0

            # Place cube 0 at (0,y,z).
            LOCATIONS.append(Location(0, y, z))
            # cube 0 orientation can be fixed because of symmetry:
            # face 0 points -x, face 3 points +x
            # face 1 points -y, face 4 points +y
            # face 2 points -z, face 5 points +z
            ORIENTATIONS.append(Orientation(Face(0), Face(1), Face(2)))

            # Recursively place the remaining cubes.
            if dfs(1):
                return
            # Backtrack: remove cube 0 from the grid.
            LOCATIONS.pop()
            ORIENTATIONS.pop()


if __name__ == "__main__":
    main()
