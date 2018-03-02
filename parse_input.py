"""
3 4 2 3 2 10
0 0 1 3 2 9
1 2 1 0 0 9
2 0 2 2 0 9

xxx
xxx
xxx
"""
from pprint import pprint

assigned_rides = set()


class Vehicle:
    def __init__(self):
        self.rides_given = []
        self.location = (0, 0)
        self.ride_start = (-1, -1)
        self.ride_earliest_start = None
        self.ride_finish = (-1, -1)
        self.started_ride = False

    @property
    def vacant(self):
        return self.ride_start[0] < 0

    @property
    def at_start(self):
        return self.location == self.ride_start

    def make_vacant(self):
        self.location = (0, 0)
        self.ride_start = (-1, -1)
        self.ride_finish = (-1, -1)
        self.started_ride = False

    @property
    def at_end(self):
        return self.location == self.ride_finish

    def move_to_start(self):
        assert self.ride_start[0] >= 0, 'Car has no destination!'

        if self.location[0] < self.ride_start[0]:
            self.location = (self.location[0] + 1, self.location[1])
        elif self.location[0] > self.ride_start[0]:
            self.location = (self.location[0] - 1, self.location[1])
        elif self.location[1] < self.ride_start[1]:
            self.location = (self.location[0], self.location[1] + 1)
        elif self.location[1] > self.ride_start[1]:
            self.location = (self.location[0], self.location[1] - 1)

    def move_to_finish(self):
        assert self.ride_finish[0] >= 0, 'Car has no destination!'

        if self.location[0] < self.ride_finish[0]:
            self.location = (self.location[0] + 1, self.location[1])
        elif self.location[0] > self.ride_finish[0]:
            self.location = (self.location[0] - 1, self.location[1])
        elif self.location[1] < self.ride_finish[1]:
            self.location = (self.location[0], self.location[1] + 1)
        elif self.location[1] > self.ride_finish[1]:
            self.location = (self.location[0], self.location[1] - 1)

    def assign_ride(self, current_time, rides, total_time):
        for ride in rides:
            if 'assigned' in ride:
                continue

            time_to_travel = total_distance(
                self.location[0], ride['start'][0], self.location[1],
                ride['start'][1], ride['distance'])
            # doable(current_time, time_to_travel, latest_finish, total_time):
            if doable(current_time, time_to_travel, ride['latest_finish'], total_time):
                assigned_rides.add(ride['index'])
                self.rides_given.append(ride['index'])
                ride['assigned'] = True
                self.ride_start = ride['start']
                self.ride_finish = ride['end']
                self.ride_earliest_start = ride['earliest_start']
                return True

        return False


def ride_distance(start_y, end_y, start_x, end_x):
    return abs(start_x - end_x) + abs(start_y - end_y)


def total_distance(start_y, current_y, start_x, current_x, ride_distance):
    return abs(start_x - current_x) + abs(start_y - current_y) + ride_distance


def doable(current_time, time_to_travel, latest_finish, total_time):
    trip_end_time = current_time + time_to_travel
    return total_time > trip_end_time < latest_finish


def on_timable(current_time, start_time, start_y, current_y, start_x, current_x):
    return current_time + abs(start_x - current_x) + abs(start_y - current_y) >= start_time


def should_consider_ride(ride, time, board_size):
    return time + ride['earliest_start'] <= board_size


def should_delete_ride(ride, time):
    return (ride['index'] in assigned_rides) or (
        ride['latest_finish'] - ride['distance'] < time)


def calculate_distance_for_rides(rides):
    for ride in rides:
        ride['distance'] = ride_distance(ride['start'][0], ride['end'][0],
                                         ride['start'][1], ride['end'][1], )


def get_shortened_list(rides, current_time, board_size):
    items_to_delete = set()
    shortened_list = []
    for i, ride in enumerate(rides):
        if should_delete_ride(ride, current_time):
            items_to_delete.add(i)
        elif should_consider_ride(ride, current_time, board_size):
            shortened_list.append(ride)

    # DELETE ITEMS Eventually
    return shortened_list


def sort_by_start_time(rides):
    return list(sorted(rides, key=lambda r: r['earliest_start']))

# sort ride list by start time
# calculate the distance of each ride
# prepare rides_to_consider:
#   for each ride, delete it if latest_finish - distance < current_time
#   skip any ride that starts later than the maximum board size (R + C)
# for each Vacant car
#   find the distance to the closest ride start that is doable (distance < time)
# send a car to destination which is before another start time


def parse_input(filename):
    with open(filename) as file:
        data = file.readlines()
    rows, columns, vehicles, rides, bonus, steps = tuple(map(int, data[0].split(' ')))
    problem_parameters = dict(
        rows=rows, columns=columns, vehicles=vehicles, rides=rides,
        bonus=bonus, steps=steps, board_size=rows + columns,
        filename_base=filename.split('.')[0]
    )
    assert rides == len(data[1:])
    ride_data = []
    for i, ride in enumerate(data[1:]):
        ride_params = tuple(map(int, ride.split(' ')))
        ride_data.append(dict(
            index=i,
            start=tuple(ride_params[0:2]),
            end=tuple(ride_params[2:4]),
            earliest_start=ride_params[4],
            latest_finish=ride_params[5],
        ))
    return problem_parameters, ride_data


def main_loop(params, rides):
    sorted_rides = sort_by_start_time(rides)
    calculate_distance_for_rides(rides)
    all_cars = [Vehicle() for _ in range(params['vehicles'])]
    max_steps = params['steps']

    for t in range(max_steps):
        print(t / max_steps * 100)
        valid_rides = get_shortened_list(sorted_rides, t, params['board_size'])

        # moment in time in our simulation
        for car in all_cars:
            if car.vacant:
                if not car.assign_ride(t, valid_rides, max_steps):
                    continue

            if car.started_ride:
                if car.at_end:
                    car.make_vacant()
                    car.assign_ride(t, valid_rides, max_steps)
                else:
                    car.move_to_finish()

            elif car.at_start:
                if car.ride_earliest_start > t:
                    pass  # wait
                else:
                    car.started_ride = True
                    car.move_to_finish()
            else:
                car.move_to_start()

            # else:
            #     # find closest starting point
            #     car.assign_ride(t, valid_rides)

        # print([car.rides_given for car in all_cars])

    output = []
    for i, car in enumerate(all_cars):
        rides_count = len(car.rides_given)
        if rides_count < 1:
            continue
        row = ' '.join([str(rides_count), ' '.join(map(str, car.rides_given))])
        output.append(row)
    result = '\n'.join(output)
    print(result)
    with open('{}.out'.format(params['filename_base']), 'w') as f:
        f.write(result)


# params, rides = parse_input('a_example.in')
# params, rides = parse_input('b_should_be_easy.in')
params, rides = parse_input('c_no_hurry.in')
# params, rides = parse_input('d_metropolis.in')
# params, rides = parse_input('e_high_bonus.in')
# pprint([params, rides])
main_loop(params, rides)
