from analysis import * 

# ==========================================
# Please use your text editor's block collapse 
# functionality ([+] icon in Notepad++) to hide
# classes and browse this file quicker.
# Fold All in Notepad++: View -> Fold Level -> 1 [Alt+1]
# ==========================================

# Ex1: "Get the frame with the most bullets (and save the screen if screenshots are on)" [only requires bullets & optionally screenshots]
class AnalysisMostBulletsFrame(Analysis):
    def __init__(self):
        self.frame_with_most_bullets = None
        self.max_bullets = 0
    
    def step(self, state: GameState):
        if state.bullets and len(state.bullets) > self.max_bullets:
            self.max_bullets = len(state.bullets)
            self.frame_with_most_bullets = state

    def done(self):
        if self.frame_with_most_bullets:
            print(f"Analysis results: frame with most bullet was stage frame #{self.frame_with_most_bullets.frame_stage} at {self.max_bullets} bullets.")
            
            if self.frame_with_most_bullets.screen is not None:
                print("Saved screenshot of frame in most_bullets.png")
                save_screenshot("most_bullets.png", self.frame_with_most_bullets.screen)
        else:
            print("No frame had any bullets.")

# Ex2: "Track the number of bullets across time and plot that as a graph" [only requires bullets]
class AnalysisBulletsOverTime(Analysis):
    def __init__(self):
        self.bulletcounts = []
    
    def step(self, state: GameState):
        if state.bullets:
            self.bulletcounts.append(len(state.bullets))

    def done(self):
        plt.plot(self.bulletcounts)
        plt.xlabel('Time (frames)')
        plt.ylabel('Bullets')
        plt.title('Bullet Count Over Time')
        plt.show()

# Ex3: "Track the number of bullets near the player across time and plot that as a graph" [only requires bullets]
class AnalysisCloseBulletsOverTime(Analysis):
    radius = 100
    
    def __init__(self):
        self.bulletcounts = []
    
    def step(self, state: GameState):
        if state.bullets:
            nearby_bullets = 0
            for bullet in state.bullets:
                if math.dist(state.player_position, bullet.position) < self.radius and bullet.is_active and (not hasattr(bullet, 'show_delay') or bullet.show_delay == 0):
                    nearby_bullets = nearby_bullets + 1

            self.bulletcounts.append(nearby_bullets)

    def done(self):
        plt.plot(self.bulletcounts)
        plt.xlabel('Time (frames)')
        plt.ylabel(f'Bullets in a {self.radius} unit radius around player')
        plt.title('Bullet Count Over Time')
        plt.show()

# Plot0: Abstract base class to factorize common plotting code
class AnalysisPlot(Analysis, ABC):
    plot_title = 'DEFAULT PLOT TITLE' #to be customized
    lastframe = None

    def __init__(self, state: GameState = None):
        self.lastframe = state

    def step(self, state: GameState):
        self.lastframe = state #if sequence, use last frame

    @abstractmethod
    def plot(self, ax, side2):
        pass #custom plot behavior to be implemented

    def done(self):
        if hasattr(self.lastframe.game_specific, 'side2') and self.lastframe.game_specific.side2:
            fig, axarr = plt.subplots(1, 2, figsize=((world_width/45) * plot_scale, 5.6 * plot_scale))
        else:
            axarr = [plt.subplots(figsize=((world_width/80) * plot_scale, 5.6 * plot_scale))[1]]

        axarr[0].set_ylabel('Y Coordinate')
        for ax in axarr:
            ax.set_xlabel('X Coordinate')
            ax.set_xlim(-world_width/2, world_width/2)
            ax.set_ylim(0, world_height)
            ax.invert_yaxis()
        plt.gcf().canvas._tkcanvas.master.title(self.plot_title)

        if len(axarr) == 2: #PvP game
            axarr[1].set_yticklabels([])
            axarr[1].set_yticks([])
            plt.suptitle(self.plot_title)
            plt.tight_layout()

            side1_res = self.plot(axarr[0], False)
            side2_res = self.plot(axarr[1], True)
            if side1_res != DONT_PLOT or (side2_res != DONT_PLOT and side2_res != HIDE_P2):
                axarr[0].set_title('Player 1')
                axarr[0].scatter(self.lastframe.player_position[0], self.lastframe.player_position[1], color='maroon', s=25*self.lastframe.player_hitbox_rad, marker='X')

                if side2_res == HIDE_P2:
                    axarr[1].axis('off')
                else:
                    axarr[1].set_title('Player 2')
                    axarr[1].scatter(self.lastframe.game_specific.side2.player_position[0], self.lastframe.game_specific.side2.player_position[1], color='maroon', s=25*self.lastframe.game_specific.side2.player_hitbox_rad, marker='X')

                plt.show()

        else:
            player_scale = self.lastframe.player_hitbox_rad
            if game_id == 14:
                player_scale *= self.lastframe.game_specific.player_scale

                if self.lastframe.game_specific.seija_flip[0] == -1:
                    axarr[0].invert_xaxis()

                if self.lastframe.game_specific.seija_flip[1] == -1:
                    axarr[0].invert_yaxis()

            elif game_id == 18:
                if self.lastframe.spellcard and self.lastframe.spellcard.spell_id == 83:
                    axarr[0].add_patch(Circle((self.lastframe.player_position[0], self.lastframe.player_position[1]), 130, color=(0.5, 0, 0.5, 0.5), fill=False))

            plt.title(self.plot_title)
            if self.plot(axarr[0], False) != DONT_PLOT:
                axarr[0].scatter(self.lastframe.player_position[0], self.lastframe.player_position[1], color='maroon', s=25*player_scale, marker='X')
                plt.show()

# Plot1: "Plot the bullet positions of the last frame at game scale (+player)" [only requires bullets]
class AnalysisPlotBullets(AnalysisPlot):
    plot_title = 'Scatter Plot of Extracted Bullet Positions'

    def plot(self, ax, side2):
        bullets = self.lastframe.game_specific.side2.bullets if side2 else self.lastframe.bullets

        if bullets:
            x_coords = [bullet.position[0] for bullet in bullets]
            y_coords = [bullet.position[1] for bullet in bullets]
            colors = [pyplot_color(get_color(bullet.bullet_type, bullet.color)) for bullet in bullets]
            sizes = [bullet.scale**2.5 * bullet.hitbox_radius * bullet_factor * pyplot_factor for bullet in bullets]
            alphas = [0.1 if not bullet.is_active or (hasattr(bullet, 'show_delay') and bullet.show_delay) else 1 for bullet in bullets]

            ax.scatter(x_coords, y_coords, color=colors, s=sizes, alpha=alphas)

        else:
            print(("(Player 2) " if side2 else "") + "No bullets to plot.")
            return DONT_PLOT

# Plot2: "Plot the enemy positions of the last frame at game scale (+player)" [only requires enemies]
class AnalysisPlotEnemies(AnalysisPlot):
    plot_title = 'Scatter Plot of Extracted Enemy Positions'

    def plot(self, ax, side2):
        enemies = self.lastframe.game_specific.side2.enemies if side2 else self.lastframe.enemies

        if enemies:
            for enemy in enemies:
                color_rgb = mcolors.to_rgba(enemy_color(enemy.anm_page, enemy.anm_id))

                if enemy.is_rectangle:
                    ax.add_patch(Rectangle( #plot rectangular enemy hitbox
                        (enemy.position[0]-enemy.hitbox[0]/2, enemy.position[1]-enemy.hitbox[1]/2),
                        width = enemy.hitbox[0] * enemy_factor * pyplot_factor,
                        height = enemy.hitbox[1] * enemy_factor * pyplot_factor,
                        angle = np.degrees(enemy.rotation),
                        facecolor = (color_rgb[0], color_rgb[1], color_rgb[2], 0.5 if enemy.no_hitbox else 1),
                        edgecolor = (0, 0, 0, 0.3), linewidth=3
                    ))

                    if plot_enemy_hurtbox:
                        ax.add_patch(Rectangle( #plot rectangular enemy hurtbox
                            (enemy.position[0]-enemy.hurtbox[0]/2, enemy.position[1]-enemy.hurtbox[1]/2),
                            width = enemy.hurtbox[0] * enemy_factor * pyplot_factor,
                            height = enemy.hurtbox[1] * enemy_factor * pyplot_factor,
                            angle = np.degrees(enemy.rotation),
                            edgecolor = (0, 0, 1, 0.2 if enemy.no_hurtbox else 0.5), linewidth=1.5, fill = False
                        ))
                else:
                    ax.add_patch(Ellipse( #plot circular enemy hitbox
                        (enemy.position[0], enemy.position[1]),
                        width = enemy.hitbox[0] * enemy_factor * pyplot_factor,
                        height = enemy.hitbox[1] * enemy_factor * pyplot_factor,
                        angle = np.degrees(enemy.rotation),
                        facecolor = (color_rgb[0], color_rgb[1], color_rgb[2], 0.5 if enemy.no_hitbox else 1),
                        edgecolor = (0, 0, 0, 0.3), linewidth=3
                    ))

                    if plot_enemy_hurtbox:
                        ax.add_patch(Ellipse( #plot circular enemy hurtbox
                            (enemy.position[0], enemy.position[1]),
                            width = enemy.hurtbox[0] * enemy_factor * pyplot_factor,
                            height = enemy.hurtbox[1] * enemy_factor * pyplot_factor,
                            angle = np.degrees(enemy.rotation),
                            edgecolor = (0, 0, 1, 0.2 if enemy.no_hurtbox else 0.5), linewidth=1.5, fill = False
                        ))

        else:
            print(("(Player 2) " if side2 else "") + "No enemies to plot.")
            return DONT_PLOT

# Plot3: "Plot the item positions of the last frame at game scale (+player)" [only requires items]
class AnalysisPlotItems(AnalysisPlot):
    plot_title = 'Scatter Plot of Extracted Item Positions'

    def plot(self, ax, side2):
        items = self.lastframe.game_specific.side2.items if side2 else self.lastframe.items

        if items:
            x_coords = [item.position[0] for item in items]
            y_coords = [item.position[1] for item in items]
            colors = [item_color(item.item_type) for item in items]
            sizes = [item_size(item.item_type) for item in items]

            ax.scatter(x_coords, y_coords, color=colors, s=sizes, marker='*')

        else:
            print(("(Player 2) " if side2 else "") + "No items to plot.")
            return DONT_PLOT

# Plot4: "Plot the line lasers of the last frame at game scale (+player)" [only requires lasers]
class AnalysisPlotLineLasers(AnalysisPlot):
    plot_title = 'Plot of Extracted Line Lasers'

    def plot(self, ax, side2):
        lasers = self.lastframe.game_specific.side2.lasers if side2 else self.lastframe.lasers
        hasLineLasers = False

        if lasers:
            for laser in lasers:
                if laser.laser_type == 0:

                    if not hasLineLasers:
                        hasLineLasers = True

                    tail_x = laser.position[0]
                    tail_y = laser.position[1]
                    head_x = tail_x + laser.length * np.cos(laser.angle)
                    head_y = tail_y + laser.length * np.sin(laser.angle)
                    ax.plot([head_x, tail_x], [head_y, tail_y], linewidth=laser.width * pyplot_factor, color=pyplot_color(get_color(laser.sprite, laser.color)), zorder=0)

                    if plot_laser_circles:
                        ax.scatter(head_x, head_y, color='white', edgecolors=pyplot_color(get_color(laser.sprite, laser.color)), s=75, zorder=1)

        if not hasLineLasers:
            print(("(Player 2) " if side2 else "") + "No line lasers to plot.")
            return DONT_PLOT

# Plot5: "Plot the infinite lasers of the last frame at game scale (+player)" [only requires lasers]
class AnalysisPlotInfiniteLasers(AnalysisPlot): 
    plot_title = 'Plot of Extracted Telegraphed Lasers'
    
    def plot(self, ax, side2):
        lasers = self.lastframe.game_specific.side2.lasers if side2 else self.lastframe.lasers
        hasInfiniteLasers = False

        if lasers:
            for laser in lasers:
                if laser.laser_type == 1:

                    if not hasInfiniteLasers:
                        hasInfiniteLasers = True

                    origin_x = laser.position[0]
                    origin_y = laser.position[1]
                    end_x = origin_x + laser.length * np.cos(laser.angle)
                    end_y = origin_y + laser.length * np.sin(laser.angle)
                    ax.plot([origin_x, end_x], [origin_y, end_y], linewidth=laser.width * pyplot_factor, color=pyplot_color(get_color(laser.sprite, laser.color)), zorder=0, alpha=(1 if laser.state==2 else 0.25))

                    if plot_laser_circles:
                        ax.scatter(origin_x, origin_y, color='white', edgecolors=pyplot_color(get_color(laser.sprite, laser.color)), s=100, zorder=1, alpha=(1 if laser.state==2 else 0.25))

        if not hasInfiniteLasers:
            print(("(Player 2) " if side2 else "") + "No telegraphed lasers to plot.")
            return DONT_PLOT

# Plot6: "Plot the curve lasers of the last frame at game scale (+player)" [only requires lasers]
class AnalysisPlotCurveLasers(AnalysisPlot):
    has_points = False
    has_line = True
    smooth = True
    smooth_steepness = 0.1

    @property
    def plot_title(self):
        return f"Plot of Extracted Curvy Lasers\nwith Points {'on' if self.has_points else 'off'}, Line {'on' if self.has_line else 'off'} and Smoothing {'on (' + str(self.smooth_steepness) + ')' if self.smooth else 'off'}"

    def __sigmoid_factor(self, x, left, right): #note: looks bad with small lasers (<15 nodes)
        shift = (self.smooth_steepness ** -1) 
        return (1 / (1 + np.exp(-self.smooth_steepness * (x - left - shift)))) * (1 / (1 + np.exp(self.smooth_steepness * (x - right + shift))))        

    def plot(self, ax, side2):
        lasers = self.lastframe.game_specific.side2.lasers if side2 else self.lastframe.lasers
        hasCurveLasers = False

        if lasers:
            for laser in lasers:
                if laser.laser_type == 2:

                    if not hasCurveLasers:
                        hasCurveLasers = True

                    if self.smooth:       
                        sizes = [laser.width * pyplot_factor * self.__sigmoid_factor(node_i, 0, len(laser.nodes)) for node_i in range(len(laser.nodes))]

                        if self.has_points:
                            x_coords = [nodes.position[0] for nodes in laser.nodes]
                            y_coords = [nodes.position[1] for nodes in laser.nodes]
                            ax.scatter(x_coords, y_coords, color=get_curve_color(laser.sprite, laser.color), s=sizes) 

                        if self.has_line:
                            for i in range(len(laser.nodes) - 1): #i hate this
                                ax.plot([laser.nodes[i].position[0], laser.nodes[i+1].position[0]], [laser.nodes[i].position[1], laser.nodes[i+1].position[1]], color=get_curve_color(laser.sprite, laser.color), linewidth=(sizes[i]+sizes[i+1])/2)
                    else: 
                        x_coords = [nodes.position[0] for nodes in laser.nodes]
                        y_coords = [nodes.position[1] for nodes in laser.nodes]

                        if self.has_points:
                            ax.scatter(x_coords, y_coords, color=get_curve_color(laser.sprite, laser.color), s=laser.width * pyplot_factor)

                        if self.has_line:
                            ax.plot(x_coords, y_coords, color=get_curve_color(laser.sprite, laser.color), linewidth=laser.width * pyplot_factor)

        if not hasCurveLasers:
            print(("(Player 2) " if side2 else "") + "No curvy lasers to plot.")
            return DONT_PLOT

# Plot7: "Plot all the above at game scale (+player)" [only doesn't require screenshots]
class AnalysisPlotAll(AnalysisPlot):
    plot_title = 'Scatter Plot of Extracted... Everything!'

    def plot(self, ax, side2):
        plottedBullets = AnalysisPlotBullets(self.lastframe).plot(ax, side2)
        plottedEnemies = AnalysisPlotEnemies(self.lastframe).plot(ax, side2)
        plottedItems = AnalysisPlotItems(self.lastframe).plot(ax, side2)
        plottedLines = AnalysisPlotLineLasers(self.lastframe).plot(ax, side2)
        plottedInfinites = AnalysisPlotInfiniteLasers(self.lastframe).plot(ax, side2)
        plottedCurves = AnalysisPlotCurveLasers(self.lastframe).plot(ax, side2)

        if plottedBullets == plottedEnemies == plottedItems == plottedLines == plottedInfinites == plottedCurves == DONT_PLOT:
            return DONT_PLOT

# Plot8: "Plot a heatmap of positions hit by bullets over time" [only requires bullets]
class AnalysisPlotBulletHeatmap(AnalysisPlot):
    circles = True #otherwise square (faster)
    max_count = 100 #prevents bullet spawn overshadowing everything, should be bigger for longer analyses

    @property
    def plot_title(self):
        return f"Bullet Heatmap w/\ncircular collision {'on' if self.circles else 'off'},\nmax bullet count capped at {self.max_count}"

    def __init__(self, state: GameState = None):
        super().__init__(state)
        self.heatmap = np.zeros((world_height + 1, world_width + 1))

    def step(self, state: GameState):
        super().step(state)
        for bullet in state.bullets:

            min_x = int(bullet.position[0] - bullet.hitbox_radius * bullet.scale + world_width/2)
            max_x = int(bullet.position[0] + bullet.hitbox_radius * bullet.scale + world_width/2)
            min_y = int(bullet.position[1] - bullet.hitbox_radius * bullet.scale)
            max_y = int(bullet.position[1] + bullet.hitbox_radius * bullet.scale)

            if min_x >= 0 and min_x <= world_width and max_x >= 0 and max_x <= world_width and min_y >= 0 and min_y <= world_height and max_y >= 0 and max_y <= world_height:
                for x in range(min_x, max_x):
                    for y in range(min_y, max_y):
                        if not self.circles or (self.circles and (x - bullet.position[0] - world_width/2) ** 2 + (y - bullet.position[1]) ** 2 <= (bullet.hitbox_radius * bullet.scale) ** 2) and self.heatmap[y, x] < self.max_count:
                            self.heatmap[y, x] += 1

    def plot(self, ax, side2):
        if side2:
            return HIDE_P2

        ax.imshow(self.heatmap, origin='lower', cmap='viridis', extent=(-world_width/2, world_width/2, 0, world_height))
        ax.figure.colorbar(ax.get_images()[0], ax=ax, label='Bullet hits')

# Bonus: "Render the bullet positions as ASCII art in the terminal" [only requires bullets] [useless]
class AnalysisPrintBulletsASCII(Analysis):
    def __init__(self):
        self.lastframe = None
        self.size_x = 90 #at this size, can be pasted into discord nicely (.txt feature makes it not take space without cutting it off much)
        self.size_y = int((self.size_x*world_height)/world_width)
        self.radius = 3 #how far to look for bullets around each where each character maps (yes it should be the other way around whatever)

    def step(self, state: GameState):
        self.lastframe = state

    def done(self):
        if not self.lastframe.bullets:
            print("No bullets to print.")
            return

        print("```")
        for y in range(0, self.size_y):
            line = ""

            for x in range(0, self.size_x):
                ingame_x = (x / self.size_x) * world_width - world_width/2
                ingame_y = (y / self.size_y) * world_height

                found = False
                for bullet in self.lastframe.bullets:
                    if math.dist((ingame_x, ingame_y), bullet.position) < self.radius:

                        if bullet.bullet_type == 20:
                            line += "☺"
                        elif bullet.bullet_type >= 38 and bullet.bullet_type <= 41:
                            line += "♪"
                        else:
                            line += "•"

                        found = True

                if not found:
                    line += " "

            print(line)
        print("```")

# LoLK: "Print on chapter transition" [no reqs.]
class AnalysisHookChapterTransition(Analysis):
    def __init__(self):
        self.time_in_chapter = 0

    def step(self, state: GameState):
        if hasattr(state.game_specific, 'time_in_chapter'):
            cur_time_in_chapter = state.game_specific.time_in_chapter
            if cur_time_in_chapter < self.time_in_chapter:
                print("Chapter Transition!!")

            self.time_in_chapter = cur_time_in_chapter

    def done(self):
        pass

# LoLK: "Plot bullets with color intensity based on graze timer" [only requires bullets]
class AnalysisPlotBulletGraze(AnalysisPlot):
    plot_title = 'Scatter Plot of Bullets w/ Graze Timer Coloring'

    def plot(self, ax, side2):
        if side2:
            return HIDE_P2

        bullets = self.lastframe.bullets

        #if any bullet has it, we're in LoLK, so they all have it
        if self.lastframe.bullets and any(hasattr(bullet, 'graze_timer') for bullet in self.lastframe.bullets):
            max_graze_timer = 0
            for bullet in self.lastframe.bullets:
                if bullet.graze_timer > max_graze_timer:
                    max_graze_timer = bullet.graze_timer

            x_coords = [bullet.position[0] for bullet in bullets]
            y_coords = [bullet.position[1] for bullet in bullets]
            sizes = [bullet.scale**2.5 * bullet.hitbox_radius * bullet_factor * pyplot_factor for bullet in bullets]
            alphas = [0.1 if not bullet.is_active or (hasattr(bullet, 'show_delay') and bullet.show_delay) else 1 for bullet in bullets]

            if max_graze_timer > 0:
                colors = [(bullet.graze_timer/max_graze_timer, 0, 0.5) for bullet in bullets]
            else:
                colors = 'C0'

            ax.scatter(x_coords, y_coords, color=colors, s=sizes, alpha=alphas)

        else:
            print("No LoLK bullets to plot.")
            return DONT_PLOT


# UM: "Find and plot the biggest mallet spot" [only requires bullets]
class AnalysisMostBulletsCircleFrame(AnalysisPlot):
    plot_title = 'Scatter Plot of Bullets w/ Best Mallet'
    mallet_player_distance = 100 

    def __init__(self):
        self.mallet_radius = 66
        self.best_bullet_count = 0
        self.best_x = -1
        self.best_y = -1
        self.step_size = 10

    def calculate_exact_count(self, center, points):
        # Count the number of points within the circle centered at center
        x_center, y_center = center
        count = 0
        for x, y in points:
            if (x - x_center) ** 2 + (y - y_center) ** 2 <= self.mallet_radius ** 2:
                count += 1
        return count

    def step(self, state: GameState):
        # Get bullet positions
        bullet_positions = [bullet.position for bullet in state.bullets if -world_width/2 <= bullet.position[0] <= world_width/2 and 0 <= bullet.position[1] <= world_height]

        # Initialize best values
        best_count = 0
        best_position = (0, 0)

        # Iterate over the grid with a certain step size
        for x in range(int(-world_width/2), int(world_width/2), self.step_size):
            for y in range(0, world_height, self.step_size):
                count = self.calculate_exact_count((x, y), bullet_positions)
                if count > best_count:
                    best_count = count
                    best_position = (x, y)

        # Update the best values
        if best_count > self.best_bullet_count:
            self.best_x, self.best_y = best_position
            self.best_bullet_count = best_count
            self.lastframe = state
        elif not self.lastframe:
            self.lastframe = state

    def plot(self, ax, side2):
        if side2:
            return HIDE_P2

        if self.best_bullet_count == 0:
            print("No frame had bullets on screen.")
            return DONT_PLOT
        
        AnalysisPlotBullets(self.lastframe).plot(ax, side2)
        AnalysisPlotLineLasers(self.lastframe).plot(ax, side2)

        ax.add_patch(Circle((self.best_x, self.best_y), self.mallet_radius, color='red', fill=False))

        print(f"Best mallet @ stage frame {self.lastframe.frame_stage} {'('+str(self.lastframe.boss_timer)+' on boss timer)' if self.lastframe.boss_timer != -1 else ''}")
        print(f"Best mallet encompases {self.best_bullet_count} bullets at ({self.best_x}, {self.best_y}); required player position ({self.best_x}, {self.best_y - self.mallet_player_distance})")
        print(f"Vanilla expected gold gain ~= {int(self.best_bullet_count*0.365692)}") #thanks to Dai for ZUN-rng distribution analysis
        print(f"Static mallet gold gain = {int(self.best_bullet_count*(11/30))}")

        print("\nNote: The first optimal solution found was displayed - it may be\nunnecessarily biased towards the left/top but remains optimal.")