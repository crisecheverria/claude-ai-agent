import os
import time
import threading
import math
import noise
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

class Colors:
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

class ASCIIOrb:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.time = 0
        self.seed = 42
        
        # Symbol sets
        self.math_symbols = '+-=*/'
        self.brackets = '()[]{}<>'
        self.symbols = '#$%&@!?'
        self.marks = '.,;:\'"`~'
        
    def get_shape_character(self, intensity, x, y, z):
        symbol_type = int((math.sin(x * 0.3 + self.time * 0.5) + 1) * 2) % 4
        pattern_shift = math.sin(y * 0.4 + z * 0.2 + self.time * 0.7) + 1
        
        symbol_sets = [self.math_symbols, self.brackets, self.symbols, self.marks]
        symbol_set = symbol_sets[symbol_type]
        
        char_index = int((intensity + pattern_shift * 0.3) * len(symbol_set))
        return symbol_set[min(char_index, len(symbol_set) - 1)]
    
    def get_orb_color(self, intensity, distance):
        hue_shift = math.sin(self.time * 0.4) * 0.5 + 0.5
        warm_shift = math.cos(self.time * 0.2 + distance) * 0.5 + 0.5
        
        if intensity < 0.15:
            return Colors.BRIGHT_BLACK
        elif intensity < 0.25:
            return Colors.BLUE
        elif intensity < 0.35:
            return Colors.MAGENTA if hue_shift > 0.6 else Colors.BLUE
        elif intensity < 0.45:
            return Colors.YELLOW if warm_shift > 0.7 else Colors.CYAN
        elif intensity < 0.55:
            return Colors.BRIGHT_YELLOW if hue_shift > 0.5 else Colors.BRIGHT_CYAN
        elif intensity < 0.65:
            return Colors.BRIGHT_MAGENTA if warm_shift > 0.6 else Colors.BRIGHT_YELLOW
        elif intensity < 0.75:
            return Colors.RED if hue_shift > 0.4 else Colors.YELLOW
        elif intensity < 0.85:
            return Colors.BRIGHT_RED if warm_shift > 0.5 else Colors.BRIGHT_MAGENTA
        else:
            return Colors.BRIGHT_WHITE if hue_shift > 0.3 else Colors.BRIGHT_YELLOW
    
    def generate_frame(self):
        output = []
        center_x = self.width / 2
        center_y = self.height / 2
        base_radius = min(self.width, self.height) / 2 * 1.2
        
        # Pulsing effect
        pulse = math.sin(self.time * 1.5) * 0.2 + 1
        orb_radius = base_radius * pulse
        
        # Rotation angles
        A = self.time * 0.8
        B = self.time * 0.5
        cos_A = math.cos(A)
        sin_A = math.sin(A)
        cos_B = math.cos(B)
        sin_B = math.sin(B)
        
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                dx = (x - center_x) * 0.5
                dy = (y - center_y) * 1.8
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance > orb_radius:
                    row += ' '
                else:
                    sphere_depth = math.sqrt(max(0, orb_radius * orb_radius - distance * distance))
                    normalized_distance = distance / orb_radius
                    
                    sphere_x = dx
                    sphere_y = dy
                    sphere_z = sphere_depth
                    
                    rotated_x = sphere_x * cos_B - sphere_z * sin_B
                    rotated_y = sphere_y * cos_A + (sphere_x * sin_B + sphere_z * cos_B) * sin_A
                    rotated_z = -sphere_y * sin_A + (sphere_x * sin_B + sphere_z * cos_B) * cos_A
                    
                    scale = 0.08
                    surface_noise = noise.pnoise3(
                        rotated_x * scale * 2 + self.time * 0.8,
                        rotated_y * scale * 2 + math.cos(self.time * 1.2) * 0.4,
                        self.seed
                    )
                    
                    detail_noise = noise.pnoise3(
                        rotated_x * scale * 8 + self.time * 1.5,
                        rotated_z * scale * 8 + math.sin(self.time * 0.9) * 0.3,
                        self.seed + 100
                    ) * 0.3
                    
                    radial_noise = noise.pnoise3(
                        rotated_y * scale * 3 + self.time * 0.6,
                        math.atan2(rotated_z, rotated_x) * 2 + self.time,
                        self.seed + 200
                    ) * 0.4
                    
                    combined_noise = surface_noise + detail_noise + radial_noise
                    lighting_factor = pow(1 - normalized_distance, 1.5)
                    depth_shading = (rotated_z + orb_radius) / (2 * orb_radius)
                    intensity = ((combined_noise + 1) / 2) * lighting_factor * depth_shading * 1.3
                    edge_falloff = pow(1 - normalized_distance, 0.5)
                    final_intensity = intensity * edge_falloff
                    
                    if final_intensity > 0.1:
                        shape_char = self.get_shape_character(final_intensity, rotated_x, rotated_y, rotated_z)
                        color = self.get_orb_color(final_intensity, normalized_distance)
                        row += color + shape_char + Colors.RESET
                    else:
                        row += ' '
            
            output.append(row)
        
        return output
    
    def update(self, dt):
        self.time += dt

class SimpleASCIIOrbChat:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.orb = ASCIIOrb()
        self.messages = []
        self.chat_history = []
        self.final_orb_frame = []
    
    def add_user_message(self, text):
        user_message = {"role": "user", "content": text}
        self.messages.append(user_message)
        self.chat_history.append(f"You: {text}")
    
    def add_assistant_message(self, text):
        assistant_message = {"role": "assistant", "content": text}
        self.messages.append(assistant_message)
        self.chat_history.append(f"🤖: {text}")
    
    def chat_with_claude(self, user_input):
        try:
            self.add_user_message(user_input)
            
            params = {
                "max_tokens": 1024,
                "model": "claude-3-5-sonnet-20241022",
                "messages": self.messages,
                "temperature": 0.7,
                "system": "You are a patient math tutor. Do not directly answer a student's question. Guide them to a solution step by step."
            }
            
            message = self.client.messages.create(**params)
            response = message.content[0].text
            
            self.add_assistant_message(response)
            return response
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.chat_history.append(error_msg)
            return error_msg
    
    def show_intro_animation(self):
        """Show intro animation for 3 seconds"""
        print(f"{Colors.BRIGHT_WHITE}🔮 Starting Claude Chat with Animated ASCII Orb ✨{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}Watch the orb animate for 3 seconds...{Colors.RESET}")
        
        for i in range(60):  # 3 seconds at 20 FPS
            print('\033[H\033[2J', end='')  # Clear screen
            print(f"{Colors.BRIGHT_WHITE}🔮 Claude Chat with Animated ASCII Orb ✨{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}Animation will stop in {3 - i//20} seconds...{Colors.RESET}")
            print(f"{Colors.BRIGHT_BLACK}{'='*80}{Colors.RESET}")
            
            self.orb.update(0.1)
            orb_lines = self.orb.generate_frame()
            
            for line in orb_lines:
                print(line)
            
            time.sleep(0.05)
        
        # Save the final frame
        self.final_orb_frame = self.orb.generate_frame()
        
        print(f"\n{Colors.BRIGHT_GREEN}Animation complete! Orb is now frozen. Ready to chat!{Colors.RESET}")
        time.sleep(1)
    
    def display_interface(self):
        print('\033[H\033[2J', end='')  # Clear screen
        
        print(f"{Colors.BRIGHT_WHITE}🔮 Claude Chat with Animated ASCII Orb ✨{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}{'='*80}{Colors.RESET}")
        
        # Use frozen orb frame
        orb_lines = self.final_orb_frame if self.final_orb_frame else [' ' * 40] * 20
        
        # Instructions on the right side only
        instructions = [
            f"{Colors.BRIGHT_CYAN}Instructions:{Colors.RESET}",
            "• Type your message and press Enter",
            "• Type 'exit' or 'quit' to close",
            "",
            "The orb shows Claude's presence"
        ]
        
        # Display orb with instructions on right
        max_lines = max(len(orb_lines), len(instructions))
        
        for i in range(max_lines):
            left_content = orb_lines[i] if i < len(orb_lines) else ' ' * 40
            right_content = instructions[i] if i < len(instructions) else ''
            
            if len(right_content) > 38:
                right_content = right_content[:35] + "..."
            
            print(f"{left_content} | {right_content}")
        
        print(f"{Colors.BRIGHT_BLACK}{'='*80}{Colors.RESET}")
        
        # Chat history below the orb
        if self.chat_history:
            print(f"{Colors.BRIGHT_CYAN}Chat History:{Colors.RESET}")
            recent_history = self.chat_history[-3:]  # Show last 3 messages
            for message in recent_history:
                # Word wrap long messages instead of truncating
                if len(message) > 78:
                    lines = []
                    words = message.split(' ')
                    current_line = ""
                    
                    for word in words:
                        if len(current_line + word + " ") <= 78:
                            current_line += word + " "
                        else:
                            if current_line:
                                lines.append(current_line.strip())
                            current_line = word + " "
                    
                    if current_line:
                        lines.append(current_line.strip())
                    
                    for line in lines:
                        print(line)
                else:
                    print(message)
                print()  # Add blank line between messages
            print(f"{Colors.BRIGHT_BLACK}{'='*80}{Colors.RESET}")
    
    def run(self):
        # Show intro animation
        self.show_intro_animation()
        
        try:
            while True:
                self.display_interface()
                
                print(f"{Colors.BRIGHT_GREEN}Enter message: {Colors.RESET}", end='')
                user_input = input().strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print(f"{Colors.BRIGHT_YELLOW}Exiting chat. Goodbye!{Colors.RESET}")
                    break
                
                if user_input:
                    print(f"{Colors.BRIGHT_MAGENTA}🤖 Thinking...{Colors.RESET}")
                    response = self.chat_with_claude(user_input)
        
        except KeyboardInterrupt:
            print(f"\n{Colors.BRIGHT_YELLOW}Chat interrupted. Goodbye!{Colors.RESET}")

if __name__ == "__main__":
    chat = SimpleASCIIOrbChat()
    chat.run()