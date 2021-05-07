from typing import Union

from gym import Env, spaces
from geometry.core.Point import Point
from geometry.core.Line import Line
from geometry.core.Circle import Circle
from geometry.core.Construction import Construction
from geometry.core.EuclidConstructions import RandomConstruction
import numpy as np


class ConstructionEnvironment(Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, boundary_radius: int = None, resolution: int = None):
        super(ConstructionEnvironment, self).__init__()
        # Define Action space
        self.resolution = resolution if resolution is not None else 32
        self.boundary_radius = boundary_radius if boundary_radius is not None else 2
        self.number_of_actions = self.resolution**4 * 2  # Resolution squared options for one pixel, pick two pixels, pick line or circle
        self.action_space = spaces.Discrete(self.number_of_actions)
        # Define observation space
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(self.resolution, self.resolution, 6), dtype=np.uint16)

        # Construction specific things
        # self.construction is the construction that we will be adding to.
        # self.desired_construction contains all the points we want.
        self.construction = Construction()
        self.construction.add_point(Point(0, 0, "A"), interesting=False)
        self.construction.add_point(Point(1, 0, "B"), interesting=False)

        # Just to emphasize, this construction could be any construction instance.
        # For now, we will initialize it as a random construction (a subclass)
        self.length = 4
        self.desired_construction: Construction = RandomConstruction(length=self.length)

    def step(self, action):
        """
        Applies the action to the environment then returns the next observation, reward, and bool representing whether the env is complete
        :param action: int representing the id of the action
        :return: next observation (np.array), reward (float), and whether_done (bool)
        """
        # Count the current missing, desired points (to calculate the reward later
        old_missing, _, _ = self._current_missing_points()

        # Perform the desired action on the construction
        self.construction.perform_action(action, self.boundary_radius, self.resolution)

        # Make sure we show the agent both the current board and the desired points
        new_missing, current_observation, desired_observation = self._current_missing_points()
        observation = np.concatenate((current_observation, desired_observation))

        # Calculate reward
        # Simple reward scheme is simply .5 points every time the agent finds a desired point and 1 point when done
        # TODO: More complex reward scheme that favors shorter constructions
        reward: float = 0
        done = False  # Have we found all the points?
        if new_missing == 0:
            reward += 1
            done = True
        reward += .5 * (old_missing - new_missing)  # Half point for every new point found

        return observation, reward, done

    def reset(self):
        # Reset the construction
        # Construction specific things
        # self.construction is the construction that we will be adding to.
        # self.desired_construction contains all the points we want.
        self.construction = Construction()
        self.construction.add_point(Point(0, 0, "A"), interesting=False)
        self.construction.add_point(Point(1, 0, "B"), interesting=False)

        # Just to emphasize, this construction could be any construction instance.
        # For now, we will initialize it as a random construction (a subclass)
        self.desired_construction: Construction = RandomConstruction(length=self.length)

        # Make sure we show the agent both the current board and the desired points
        _, current_observation, desired_observation = self._current_missing_points()
        observation = np.concatenate((current_observation, desired_observation))
        return observation

    def render(self, mode='human'):
        self.construction.plain_text(self.boundary_radius, self.resolution)
        self.desired_construction.plain_text(self.boundary_radius, self.resolution)

    def _current_missing_points(self) -> (int, np.array, np.array):
        """
        Count how many points in self.desired_construction are missing in self.construction
        :return: int representing the number of missing points
        :return: np.array representing the current observations
        :return: np.array representing the desired observations
        """
        # Make sure we show the agent both the current board and the desired points
        current_observation = self.construction.numpy(self.boundary_radius, self.resolution)
        desired_observation = self.desired_construction.numpy(self.boundary_radius, self.resolution, interesting=True)
        # observation = np.concatenate((current_observation, desired_observation))

        # Take the desired points (binary) and subtract current points.
        # Then get rid of any negatives (meaning there were extra points).
        # If there are any 1's left, then we haven't found that pixel.
        difference_matrix = desired_observation[0] - current_observation[0]
        difference_matrix[difference_matrix < 0] = 0
        return np.count_nonzero(difference_matrix), current_observation, desired_observation

    @staticmethod
    def _point_to_image_space(point: Union[Point, np.array], boundary_radius: int, resolution: int) -> np.array:
        origin = np.array([resolution / 2, resolution / 2])
        if type(point) is Point:
            point = point.numpy()
        return (point * resolution / (2 * boundary_radius) + origin).round().astype(np.uint16)

    @staticmethod
    def _points_to_action_number(point1: np.array, point2: np.array, is_line: bool, boundary_radius: int, resolution: int):
        # If either of the points do not exist, return 0 action
        if point1 is None or point2 is None:
            return 0
        # Otherwise, convert to image (pixel) space coordinates
        point1 = ConstructionEnvironment._point_to_image_space(point1, boundary_radius, resolution)
        point2 = ConstructionEnvironment._point_to_image_space(point2, boundary_radius, resolution)


        # Start with action=0. We will encode the actions as an integer.
        action = 0
        action += point2[1] * resolution**4
        action += point2[0] * resolution**3
        action += point1[1] * resolution**2
        action += point1[0] * resolution
        action = int(action)

        # We define the last bit to be whether or not the action is drawing a line.
        # True = line, False = circle
        action = action << 1
        if is_line:
            action += 1

        return action

    def legal_actions(self):
        """
        Should return the legal actions at each turn, if it is not available, it can return
        the whole action space. At each turn, the game have to be able to handle one of returned actions.

        For complex game where calculating legal moves is too long, the idea is to define the legal actions
        equal to the action space but to return a negative reward if the action is illegal.
        Returns:
            An array of integers, subset of the action space.
        """
        legal_moves: {int} = set()  # List of integers showing legal moves
        for point1 in self.construction.points:
            for point2 in self.construction.points:
                if point1 is not point2:
                    # TODO: This may slow down training if the network thinks line(A,B) != line(B,A), but legal
                    #  actions thinks they are the same
                    if Line(point1, point2) not in self.construction.lines:
                        legal_moves.add(self._points_to_action_number(point1, point2, True,
                                                                      self.boundary_radius, self.resolution))
                    if Circle(center=point1, point2=point2) not in self.construction.circles:
                        legal_moves.add(self._points_to_action_number(point1, point2, False,
                                                                      self.boundary_radius, self.resolution))
                    if Circle(center=point2, point2=point1) not in self.construction.circles:
                        legal_moves.add(self._points_to_action_number(point2, point1, False,
                                                                      self.boundary_radius, self.resolution))

        return list(legal_moves)

    def action_to_string(self, action_number):
        """
        Convert an action number to a string representing the action.
        Args:
            action_number: an integer from the action space.
        Returns:
            String representing the action.
        """
        is_line, point1, point2 = self.construction._interpret_action(action_number, self.boundary_radius,

                                                                      self.resolution)
        if is_line:
            # If a line, then we simply return the point names with overbars
            return f'{point1.name}\u0305{point2.name}\u0305'
        else:
            # If a circle, then we return in the format "c A r AB"
            return f'\u25ef{point1.name}r{point1.name}\u0305{point2.name}\u0305'