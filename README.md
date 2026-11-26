# myrepo

> **项目说明：** 本项目是一个先验的学习项目，主要用于练习和验证基础概念、技术方案与实验性想法，不保证可直接用于生产环境。

## 波浪模拟

`wave_simulation.py` 提供基于线性叠加的波高计算函数。每个波浪分量由振幅、波数、角频率和可选初相位描述：

```python
from wave_simulation import WaveComponent, calculate_wave_height

waves = [
    WaveComponent(amplitude=1.0, wave_number=2.0, angular_frequency=0.5),
    WaveComponent(amplitude=0.3, wave_number=1.2, angular_frequency=0.8, phase=0.4),
]

height = calculate_wave_height(x=10.0, time=3.0, waves=waves)
```

### 浏览器演示

使用 Python 启动本地服务：

```bash
python wave_server.py
```

然后打开 <http://127.0.0.1:8000>。演示页面会定期调用 `POST /api/wave-height`，请求体包含 `time`、`positions` 和 `waves`，响应为对应位置的波高采样值。