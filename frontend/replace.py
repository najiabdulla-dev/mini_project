import os
import re

lib_dir = r'c:\movies\skill-trade\frontend\lib'

for root, dirs, files in os.walk(lib_dir):
    for file in files:
        if file.endswith('.dart'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            orig_content = content
            
            # Replace `const AppColors.xxx` with `AppColors.xxx`
            content = re.sub(r'const\s+AppColors\.', 'AppColors.', content)
            
            if content != orig_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

print("Done fixing const AppColors.")
