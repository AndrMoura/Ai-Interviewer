import { useState } from 'react';

const ColorToggle = () => {
  const [color, setColor] = useState('red');

  const handleColorChange = () => {
    const colors = ['red', 'orange', 'yellow'];

    const currentIndex = colors.indexOf(color);
    console.log("Call")
    if (currentIndex !== -1) {
      setColor(colors[(currentIndex + 1) % colors.length]);
      console.log("")
    }
  };

  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <button onClick={handleColorChange}>Toggle Color</button>
      <div
        style={{
          width: '200px',
          height: '200px',
          borderRadius: '50%',
          backgroundColor: color,
          marginTop: '20px',
        }}
      />
    </div>
  );
};

export default ColorToggle;