import pymunk
import pygame
from pymunk.vec2d import Vec2d
import random
from pymunk.pygame_util import DrawOptions
from tqdm import tqdm

# Create a pymunk space
space = pymunk.Space()
space.gravity = (0, 1000)  # Set the gravity

def add_joint(b, b2, a=(0, 0), a2=(0, 0), collide=True):
    joint = pymunk.PivotJoint(b, b2, a, a2)
    joint.distance = 0
    joint.collide_bodies = collide
    space.add(joint)

def add_bar(space, pos, thickness=10, length=80):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Segment(body, (0, 0), (length, 0), thickness)
    shape.mass = 2
    shape.friction = 0.7
    shape.density = 0.1
    shape.elasticity = 0.5
    shape.filter = pymunk.ShapeFilter(group=1)
    shape.color = (0, 0, 255, 0)
    space.add(body, shape)
    return body, shape

def add_ground(space):
    ground = pymunk.Segment(space.static_body, (0, 600), (8000, 600), 200)
    ground.friction = 0.5
    ground.elasticity = 1
    ground.color = (0, 255, 0, 0)
    space.add(ground)
    return ground

size = w, h = 1000, 800

def simulation(n_sticks, random_rotations, display=False, time=500):
    if display:
        pygame.font.init()
        font = pygame.font.SysFont('Arial', 30)
    
    n_joints = n_sticks - 1
    sticks = []
    joints = []
    ground = add_ground(space)
    p = Vec2d(400, 300)
    
    for i in range(n_sticks):
        stick = add_bar(space, p + (i * 80, 0))
        sticks.append(stick)
        
    for i in range(n_joints):
        joint = add_joint(sticks[i][0], sticks[i+1][0], (80, 0), (0, 0))
        joints.append(joint)
        
    if display:
        pygame.init()
        screen = pygame.display.set_mode(size)
        draw_options = DrawOptions(screen)
    clock = pygame.time.Clock()
    
    index = 0
    count = 0
    running = True
    while running:
        if display:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return 0, random_rotations, n_sticks

        count += 1
        if count % 60 == 0:
            index += 1
            index %= 3
        if count > time:
            running = False
            for shape in space.shapes:
                space.remove(shape)
            for body in space.bodies:
                space.remove(body)
            for constraint in space.constraints:
                space.remove(constraint)
            if display:
                pygame.quit()
            return distance

        if display:
            screen.fill((220, 220, 220))
            
        stick_pos = sticks[0][0].position
        for stick in sticks:
            stick[0].angular_velocity = random_rotations[sticks.index(stick)][index]
            
        dt = 1.0 / 60.0
        space.step(dt)
        distance = (stick_pos.x - 400) / 100

        if display:
            # Create a transformation that translates the origin to the position of the stick
            transform = pymunk.Transform(tx=-stick_pos.x + size[0] // 2, ty=-stick_pos.y + size[1] // 2)
            # Create a DebugDraw object
            draw_options = pymunk.pygame_util.DrawOptions(screen)
            # Set the transformation of the DebugDraw object
            draw_options.transform = transform
            
            space.debug_draw(draw_options)
            distance_text = font.render('Distance: {:.2f}'.format(distance), True, (0, 0, 0))
            screen.blit(distance_text, (10, 10))
            pygame.display.flip()
            clock.tick(60)

best_results = []
for i in range(100):
    best_distance = 0
    for j in range(50):
        n_sticks = random.randint(1, 5)
        random_rotations = [[random.uniform(-3, 3) for k in range(3)] for _ in range(n_sticks)]
        distance = simulation(n_sticks, random_rotations, display=False)
        if distance > best_distance:
            best_distance = distance
            best_movement = random_rotations
            best_nb_sticks = n_sticks
    best_results.append([best_distance, best_movement, best_nb_sticks])

for generation in range(100):
    mutants = []
    for result in tqdm(best_results):
        best_distance = result[0]
        best_movement = result[1]
        best_nb_sticks = result[2]
            
        for i in range(200):
            nb_sticks = best_nb_sticks
            mutated_movement = [[best_movement[j][k] + random.uniform(-0.5, 0.5) if random.random() < 0.5 else best_movement[j][k] for k in range(3)] for j in range(nb_sticks)]
            
            proba = random.random()
            if proba < 0.25 and nb_sticks < 5:
                nb_sticks += 1
                mutated_movement.append([random.uniform(-3, 3) for k in range(3)])
            elif proba < 0.5 and nb_sticks > 1:
                nb_sticks -= 1
                mutated_movement.pop()
                
            distance = simulation(nb_sticks, mutated_movement, display=False)
            
            if distance > best_distance:
                best_distance = distance
                best_movement = mutated_movement
                best_nb_sticks = nb_sticks
                    
        mutants.append([best_distance, best_movement, best_nb_sticks])

    best_mutant = max(mutants, key=lambda x: x[0])
    print("Best mutant: ", best_mutant)
    
    simulation(best_mutant[2], best_mutant[1], display=True, time=1500)
    
    # Select the 100 best mutants and make them evolve again !
    best_results = sorted(mutants, key=lambda x: x[0], reverse=True)[:100]
