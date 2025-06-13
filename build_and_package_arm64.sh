#!/bin/bash

echo "🔨 Building Aleksameter application..."
pyinstaller Aleksameter_mac_arm64.spec

if [ $? -eq 0 ]; then
    echo "✅ Application build successful!"
    echo "📦 Creating DMG package..."
    ./make_dmg.sh
    
    if [ $? -eq 0 ]; then
        echo "🎉 DMG package created successfully!"
        echo "📁 Location: $(pwd)/Aleksameter_mac_arm64.dmg"
        echo "📊 Size: $(du -sh Aleksameter_mac_arm64.dmg | cut -f1)"
    else
        echo "❌ DMG creation failed!"
        exit 1
    fi
else
    echo "❌ Application build failed!"
    exit 1
fi 