import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, useSpring } from 'framer-motion';
import Plot from 'react-plotly.js';
import axios from 'axios';
import {
  Search, Calendar, Zap, Shield, GraduationCap,
  ArrowUpRight, ArrowDownRight, Activity, Copy,
  ChevronDown, ChevronUp, AlertTriangle, CheckCircle, BarChart2
} from 'lucide-react';

// Use environment variable in production, localhost in development
const API_URL = import.meta.env.VITE_API_URL || (
  window.location.hostname === 'localhost'
    ? 'http://localhost:8001'
    : window.location.origin
);

// --- 1. PARTICLE BACKGROUND & MOUSE TRACKER ---
const ParticleBackground = () => {
  const particles = useMemo(() => Array.from({ length: 30 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 4 + 2,
    duration: Math.random() * 20 + 10,
    delay: Math.random() * 5
  })), []);

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-accent-cyan/20 blur-[1px]"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
          }}
          animate={{
            y: [0, -100, 0],
            opacity: [0, 0.5, 0],
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      ))}
    </div>
  );
};

const MouseTracker = () => {
  useEffect(() => {
    const handleMouseMove = (e) => {
      const x = (e.clientX / window.innerWidth) * 100;
      const y = (e.clientY / window.innerHeight) * 100;
      document.body.style.setProperty('--mouse-x', `${x}%`);
      document.body.style.setProperty('--mouse-y', `${y}%`);
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);
  return null;
};

// --- 2. HERO SECTION (Revolut Style) ---
const HeroSection = ({ ticker, livePrice }) => {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useTransform(y, [-100, 100], [10, -10]);
  const rotateY = useTransform(x, [-100, 100], [-10, 10]);
  const [timePeriod, setTimePeriod] = useState('1D');
  const [chartData, setChartData] = useState(null);
  const [loadingChart, setLoadingChart] = useState(false);

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;
    x.set(xPct * 200);
    y.set(yPct * 200);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  const periods = ['5M', '15M', '1H', '1D', '1W', '1M', '1Y'];

  // Map periods to Yahoo Finance API intervals and ranges
  const periodConfig = useMemo(() => ({
    '5M': { interval: '1m', range: '1d' },
    '15M': { interval: '5m', range: '1d' },
    '1H': { interval: '15m', range: '5d' },
    '1D': { interval: '1h', range: '1d' },
    '1W': { interval: '1d', range: '5d' },
    '1M': { interval: '1d', range: '1mo' },
    '1Y': { interval: '1d', range: '1y' }
  }), []);

  // Fetch chart data when ticker or time period changes
  useEffect(() => {
    const fetchChartData = async () => {
      if (!ticker) {
        console.log('No ticker provided');
        return;
      }

      console.log(`Fetching chart for ${ticker}, period: ${timePeriod}`);
      setLoadingChart(true);

      try {
        const config = periodConfig[timePeriod];
        console.log('Config:', config);

        // Use our backend proxy endpoint to avoid CORS issues
        const response = await axios.get(`${API_URL}/api/chart/${ticker}`, {
          params: {
            interval: config.interval,
            range: config.range
          }
        });

        console.log('API Response:', response.data);

        if (response.data.success && response.data.data.points) {
          // Convert timestamps to dates
          const chartPoints = response.data.data.points.map(point => ({
            time: new Date(point.timestamp * 1000),
            price: point.price
          }));

          console.log(`Chart data: ${chartPoints.length} points`);
          setChartData(chartPoints);
        } else {
          console.error('No chart data in response');
          setChartData(null);
        }
      } catch (err) {
        console.error('Failed to fetch chart data:', err);
        console.error('Error details:', err.response?.data || err.message);
        setChartData(null);
      } finally {
        setLoadingChart(false);
      }
    };

    fetchChartData();
  }, [ticker, timePeriod, periodConfig]);

  return (
    <section className="relative min-h-[60vh] flex flex-col items-center justify-center pt-24 pb-12 z-10">
      <motion.div
        className="text-center mb-12 space-y-4"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surfaceHighlight/50 border border-white/10 backdrop-blur-md mb-4">
          <span className="w-2 h-2 rounded-full bg-accent-green animate-pulse"></span>
          <span className="text-xs text-gray-400 font-mono tracking-wide">SYSTEM ONLINE • v2.4.0</span>
        </div>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white">
          Option-Implied <br />
          <span className="text-gradient">PDF Visualizer</span>
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto">
          Decode institutional-grade probability distributions from real-time options data using Breeden-Litzenberger extraction.
        </p>
      </motion.div>

      <motion.div
        style={{ rotateX, rotateY, perspective: 1000 }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3, duration: 0.8 }}
        className="relative w-full max-w-3xl aspect-[16/9] mx-4"
      >
        <div className="absolute inset-0 bg-gradient-to-tr from-accent-cyan/20 to-accent-purple/20 blur-3xl rounded-full opacity-30 animate-blob" />
        <div className="glass-card w-full h-full rounded-3xl p-8 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />

          {/* Mini Price Chart */}
          <div className="flex flex-col h-full">
            <div className="flex-1 relative">
              {loadingChart ? (
                <div className="flex items-center justify-center h-full">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-cyan"></div>
                </div>
              ) : chartData && chartData.length > 0 ? (
                (() => {
                  // Calculate tight y-axis range
                  const prices = chartData.map(d => d.price);
                  const minPrice = Math.min(...prices);
                  const maxPrice = Math.max(...prices);
                  const range = maxPrice - minPrice;

                  // Add 0.5% padding on each side for better visibility
                  const padding = range * 0.005;
                  const yMin = minPrice - padding;
                  const yMax = maxPrice + padding;

                  return (
                    <Plot
                      data={[
                        {
                          x: chartData.map(d => d.time),
                          y: prices,
                          type: 'scatter',
                          mode: 'lines',
                          line: {
                            color: livePrice?.change >= 0 ? '#00ff88' : '#ff4757',
                            width: 2,
                            shape: 'spline'
                          },
                          fill: 'tozeroy',
                          fillcolor: livePrice?.change >= 0 ? 'rgba(0, 255, 136, 0.1)' : 'rgba(255, 71, 87, 0.1)',
                          hovertemplate: '<b>%{y:.2f}</b><br>%{x}<extra></extra>'
                        }
                      ]}
                      layout={{
                        autosize: true,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        margin: { l: 50, r: 60, t: 10, b: 40 },
                        xaxis: {
                          gridcolor: 'rgba(255,255,255,0.05)',
                          showticklabels: true,
                          tickfont: { color: '#a0a0a0', size: 11 },
                          tickformat: timePeriod === '1Y' ? '%b %Y' : timePeriod === '1M' ? '%b %d' : '%H:%M',
                          zeroline: false,
                          showgrid: true
                        },
                        yaxis: {
                          gridcolor: 'rgba(255,255,255,0.05)',
                          showticklabels: true,
                          tickfont: { color: '#a0a0a0', size: 11 },
                          tickprefix: '$',
                          tickformat: '.2f',
                          zeroline: false,
                          side: 'right',
                          showgrid: true,
                          automargin: true,
                          range: [yMin, yMax],
                          fixedrange: false
                        },
                        hoverlabel: {
                          bgcolor: '#1e1e2e',
                          bordercolor: '#00d9ff',
                          font: { color: '#ffffff', size: 12, family: 'JetBrains Mono' }
                        },
                        showlegend: false,
                        hovermode: 'x unified'
                      }}
                      useResizeHandler={true}
                      style={{ width: "100%", height: "100%" }}
                      config={{ displayModeBar: false, responsive: true }}
                    />
                  );
                })()

              ) : (
                <div className="flex items-center justify-center h-full">
                  <Activity size={64} className="text-accent-cyan opacity-40" />
                </div>
              )}
            </div>

            {/* Price Info & Controls */}
            <div className="space-y-3">
              {/* Current Price */}
              <div className="flex justify-between items-end font-mono">
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Current Price</div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold text-white">{ticker || 'SPY'}</span>
                    <span className={`text-lg ${livePrice?.change >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                      ${livePrice?.price || '---'}
                    </span>
                    <span className={`text-sm ${livePrice?.change >= 0 ? 'text-accent-green' : 'text-accent-red'} flex items-center gap-1`}>
                      {livePrice?.change >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                      {livePrice?.changePercent || '--'}%
                    </span>
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-accent-green animate-pulse"></span>
                    LIVE FEED
                  </span>
                </div>
              </div>

              {/* Time Period Selector */}
              <div className="flex gap-1 p-1 bg-surface/30 rounded-lg">
                {periods.map(period => (
                  <button
                    key={period}
                    onClick={() => setTimePeriod(period)}
                    className={`flex-1 px-2 py-1 text-xs font-medium rounded transition-all ${
                      timePeriod === period
                        ? 'bg-accent-cyan/20 text-accent-cyan'
                        : 'text-gray-500 hover:text-gray-300'
                    }`}
                  >
                    {period}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
};

// --- 3. INPUT CONTROLS (Linear Speed) ---
const InputControls = ({ onRunAnalysis, ticker, setTicker, dte, setDte, mode, setMode, loading }) => {
  const modes = [
    { value: "standard", label: "Standard", icon: "📊" },
    { value: "conservative", label: "Conservative", icon: "🛡️" },
    { value: "aggressive", label: "Aggressive", icon: "⚡" },
    { value: "educational", label: "Educational", icon: "🎓" }
  ];

  const tickers = [
    { value: "SPY", label: "SPY - S&P 500 ETF" },
    { value: "QQQ", label: "QQQ - Nasdaq 100 ETF" },
    { value: "AAPL", label: "AAPL - Apple Inc." },
    { value: "MSFT", label: "MSFT - Microsoft" },
    { value: "TSLA", label: "TSLA - Tesla" },
    { value: "NVDA", label: "NVDA - Nvidia" },
    { value: "AMZN", label: "AMZN - Amazon" },
    { value: "GOOGL", label: "GOOGL - Alphabet" },
    { value: "META", label: "META - Meta Platforms" },
    { value: "IWM", label: "IWM - Russell 2000 ETF" }
  ];

  return (
    <div className="w-full max-w-5xl mx-auto mb-16 px-4 z-20 relative">
      <motion.div
        className="glass-card rounded-2xl p-1"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="grid grid-cols-1 md:grid-cols-4 gap-2 bg-primary/40 rounded-xl p-2">
          {/* Ticker Selector */}
          <div className="relative group">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-accent-cyan z-10 pointer-events-none">
              <Search size={18} />
            </div>
            <select
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              className="w-full h-14 bg-surface/50 border border-white/5 rounded-lg pl-12 pr-8 text-white font-mono appearance-none cursor-pointer hover:bg-surface/80 transition-colors focus:outline-none focus:border-accent-cyan/50"
            >
              <option value="" disabled className="text-gray-500">Select Ticker</option>
              {tickers.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
            <ChevronDown size={16} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
          </div>

          {/* DTE Selector */}
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
              <Calendar size={18} />
            </div>
            <select
              value={dte}
              onChange={(e) => setDte(e.target.value)}
              className="w-full h-14 bg-surface/50 border border-white/5 rounded-lg pl-12 pr-8 text-white appearance-none cursor-pointer hover:bg-surface/80 transition-colors focus:outline-none focus:border-accent-cyan/50"
            >
              <option value="" disabled className="text-gray-500">Days to Expiry</option>
              <option value="7">7 Days</option>
              <option value="30">30 Days (Recommended)</option>
              <option value="45">45 Days</option>
              <option value="90">90 Days</option>
            </select>
            <ChevronDown size={16} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
          </div>

          {/* Analysis Mode Dropdown */}
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
              <Shield size={18} />
            </div>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              disabled={loading}
              className="w-full h-14 bg-surface/50 border border-white/5 rounded-lg pl-12 pr-8 text-white appearance-none cursor-pointer hover:bg-surface/80 transition-colors focus:outline-none focus:border-accent-cyan/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value="" disabled className="text-gray-500">Analysis Mode</option>
              {modes.map(m => (
                <option key={m.value} value={m.value}>{m.icon} {m.label}</option>
              ))}
            </select>
            <ChevronDown size={16} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
          </div>

          {/* Analyze Button */}
          <motion.button
            whileHover={!loading ? { scale: 1.02 } : {}}
            whileTap={!loading ? { scale: 0.98 } : {}}
            onClick={onRunAnalysis}
            disabled={loading}
            className={`h-14 px-8 bg-gradient-to-r from-accent-cyan to-blue-600 rounded-lg font-bold text-primary flex items-center justify-center gap-2 shadow-glow-cyan ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Zap size={18} fill="currentColor" />
                <span>Analyze</span>
              </>
            )}
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
};

// --- 4. METRIC CARDS (Netflix Reveal) ---
const MetricCards = ({ data }) => {
  // Calculate expected price direction (for directional bias)
  const expectedChange = ((data.statistics.mean - data.spot_price) / data.spot_price * 100).toFixed(2);
  const expectedChangeColor = expectedChange >= 0 ? 'text-accent-green' : 'text-accent-red';

  // Bias based on expected price direction (not skewness)
  const bias = expectedChange >= 0 ? 'Bullish' : 'Bearish';
  const biasColor = expectedChange >= 0 ? 'border-accent-green' : 'border-accent-red';
  const biasTextColor = expectedChange >= 0 ? 'text-accent-green' : 'text-accent-red';
  const biasIcon = expectedChange >= 0 ? <ArrowUpRight size={16}/> : <ArrowDownRight size={16}/>;

  const metrics = [
    { label: 'Spot Price', value: `$${data.spot_price.toFixed(2)}`, color: 'border-accent-cyan', text: 'text-accent-cyan', sub: 'Current Underlying', icon: <Activity size={16}/> },
    { label: 'Expected Price', value: `$${data.statistics.mean.toFixed(2)}`, color: 'border-accent-green', text: expectedChangeColor, sub: `${expectedChange >= 0 ? '+' : ''}${expectedChange}% (Risk Neutral)`, icon: <ArrowUpRight size={16}/> },
    { label: 'Implied Move', value: `±${data.statistics.implied_move_pct.toFixed(2)}%`, color: 'border-accent-purple', text: 'text-accent-purple', sub: `$${data.statistics.ci_lower.toFixed(0)} - $${data.statistics.ci_upper.toFixed(0)} (1σ)`, icon: <BarChart2 size={16}/> },
    { label: 'Market Bias', value: bias, color: biasColor, text: biasTextColor, sub: `Skew: ${data.statistics.skewness.toFixed(2)}`, icon: biasIcon }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      {metrics.map((m, i) => (
        <motion.div
          key={m.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 + 0.5 }}
          whileHover={{ y: -5, boxShadow: "0 10px 30px -10px rgba(0,0,0,0.5)" }}
          className={`glass-card rounded-2xl p-6 border-t-2 ${m.color}`}
        >
          <div className="flex justify-between items-start mb-4">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">{m.label}</span>
            <div className={`p-2 rounded-lg bg-white/5 ${m.text}`}>
              {m.icon}
            </div>
          </div>
          <div className="text-3xl font-mono font-bold text-white mb-1">{m.value}</div>
          <div className="text-xs text-gray-400">{m.sub}</div>
        </motion.div>
      ))}
    </div>
  );
};

// --- 5. INTERACTIVE CHART (Plotly Wrapper) ---
const PDFChart = ({ data }) => {
  const x = data.pdf.strikes;
  const y = data.pdf.values;
  const spot = data.spot_price;

  return (
    <motion.div
      className="glass-card rounded-3xl p-1 mb-8 overflow-hidden"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, delay: 0.8 }}
    >
      <div className="bg-primary/40 rounded-2xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <BarChart2 className="text-accent-cyan" size={20} />
            Probability Distribution Function ({data.days_to_expiry}D)
          </h3>
          <span className="flex items-center gap-2 text-xs text-accent-green bg-accent-green/10 px-3 py-1 rounded-full border border-accent-green/20">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-green opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-green"></span>
            </span>
            LIVE DATA
          </span>
        </div>
        <div className="h-[400px] w-full">
          <Plot
            data={[
              {
                x: x,
                y: y,
                type: 'scatter',
                mode: 'lines',
                fill: 'tozeroy',
                line: { color: '#00d9ff', width: 3, shape: 'spline' },
                fillcolor: 'rgba(0, 217, 255, 0.1)',
                name: 'Probability'
              },
              {
                x: [spot, spot],
                y: [0, Math.max(...y)],
                type: 'scatter',
                mode: 'lines',
                line: { color: '#00ff88', width: 2, dash: 'dash' },
                name: 'Spot Price'
              }
            ]}
            layout={{
              autosize: true,
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
              margin: { l: 60, r: 20, t: 20, b: 50 },
              xaxis: {
                gridcolor: '#2a2a3e',
                title: { text: 'Strike Price ($)', font: { color: '#ffffff', size: 13 } },
                tickfont: { color: '#ffffff', size: 12 },
                showgrid: true
              },
              yaxis: {
                gridcolor: '#2a2a3e',
                title: { text: 'Probability Density', font: { color: '#ffffff', size: 13 } },
                tickfont: { color: '#ffffff', size: 12 },
                showgrid: true,
                automargin: true
              },
              hoverlabel: {
                bgcolor: '#1e1e2e',
                bordercolor: '#00d9ff',
                font: { color: '#ffffff', size: 14, family: 'JetBrains Mono' }
              },
              showlegend: false,
              hovermode: 'x unified',
            }}
            useResizeHandler={true}
            style={{ width: "100%", height: "100%" }}
            config={{ displayModeBar: false }}
          />
        </div>
      </div>
    </motion.div>
  );
};

// --- 6. AI INSIGHTS (Apple Style) ---
const AIInsights = ({ data }) => {
  const interpretation = data.interpretation || "";

  // Check if this is a fallback/generic interpretation
  const isFallback = interpretation.includes('fallback analysis') ||
                      interpretation.includes('unavailable') ||
                      !interpretation.trim();

  // Generate accurate analysis based on actual statistics
  const generateAnalysis = () => {
    const stats = data.statistics;
    const bias = stats.skewness < 0 ? 'bearish' : 'bullish';
    const biasStrength = Math.abs(stats.skewness) > 1 ? 'strongly' :
                         Math.abs(stats.skewness) > 0.5 ? 'moderately' : 'slightly';

    const expectedMove = ((stats.mean - data.spot_price) / data.spot_price * 100);
    const moveDirection = expectedMove >= 0 ? 'upward' : 'downward';

    const kurtosisLevel = stats.kurtosis > 3 ? 'elevated' :
                          stats.kurtosis < 3 ? 'reduced' : 'normal';
    const tailRisk = stats.kurtosis > 3 ? 'higher than normal' : 'within normal range';

    return [
      `<strong>Market Sentiment:</strong> The distribution shows a ${biasStrength} ${bias} bias with a skewness of ${stats.skewness.toFixed(2)}. The implied ${moveDirection} move of ${Math.abs(expectedMove).toFixed(2)}% suggests the market expects ${data.ticker} to trade around $${stats.mean.toFixed(2)} by expiration.`,

      `<strong>Volatility Assessment:</strong> The implied move of ±${stats.implied_move_pct.toFixed(2)}% indicates ${stats.implied_move_pct > 5 ? 'elevated' : stats.implied_move_pct > 3 ? 'moderate' : 'low'} volatility expectations. The 68% confidence interval spans from $${stats.ci_lower.toFixed(2)} to $${stats.ci_upper.toFixed(2)}.`,

      `<strong>Tail Risk:</strong> Fat tail analysis (kurtosis=${stats.kurtosis.toFixed(2)}) indicates ${kurtosisLevel} probability of extreme moves, with tail risk ${tailRisk}. This suggests ${stats.kurtosis > 3 ? 'higher probability of large unexpected moves than a normal distribution would predict' : 'extreme moves are less likely than normal distribution'}.`,

      `<strong>Key Takeaway:</strong> Markets are pricing ${bias} sentiment with ${stats.implied_move_pct > 5 ? 'significant' : 'moderate'} expected volatility over the next ${data.days_to_expiry} days.`
    ];
  };

  const paragraphs = isFallback ? generateAnalysis() : interpretation.split('\n\n').filter(p => p.trim());
  const title = isFallback ? 'Statistical Analysis' : 'AI Market Intelligence';
  const subtitle = isFallback
    ? `Generated from ${data.analysis_mode} mode statistics using ${data.interpolation_method} interpolation`
    : `Powered by ${data.analysis_mode} analysis mode using ${data.interpolation_method} interpolation`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1 }}
      className="glass-card rounded-2xl p-6 mb-8"
    >
      <div className="flex items-start gap-4 mb-6">
        <div className="p-3 rounded-xl bg-accent-cyan/10 border border-accent-cyan/20">
          <Shield className="text-accent-cyan" size={24} />
        </div>
        <div className="flex-1">
          <h3 className="text-2xl font-bold mb-2">{title}</h3>
          <p className="text-sm text-gray-400">{subtitle}</p>
          {isFallback && (
            <p className="text-xs text-yellow-500 mt-1">
              ⚠ AI interpretation unavailable - showing statistical analysis
            </p>
          )}
        </div>
      </div>

      <div className="prose prose-invert max-w-none space-y-3">
        {paragraphs.map((para, i) => {
          // Convert markdown to HTML
          let cleanedPara = para
            .replace(/###\s+(.+)/g, '<h3 class="text-lg font-bold text-accent-cyan mb-2 mt-4">$1</h3>')
            .replace(/##\s+(.+)/g, '<h2 class="text-xl font-bold text-accent-cyan mb-2 mt-4">$1</h2>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>');

          return (
            <div
              key={i}
              className="text-gray-300 leading-relaxed"
              dangerouslySetInnerHTML={{ __html: cleanedPara }}
            />
          );
        })}
      </div>

      <div className="mt-6 pt-6 border-t border-white/10 grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Tail Risk (Down 10%)</span>
          <div className="text-accent-red font-mono text-lg">
            {data.statistics.tail_prob_down_10pct
              ? (data.statistics.tail_prob_down_10pct * 100).toFixed(2)
              : '0.00'}%
          </div>
        </div>
        <div>
          <span className="text-gray-500">Tail Risk (Up 10%)</span>
          <div className="text-accent-green font-mono text-lg">
            {data.statistics.tail_prob_up_10pct
              ? (data.statistics.tail_prob_up_10pct * 100).toFixed(2)
              : '0.00'}%
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// --- 7. DATA TABLE (Stripe Quality) - Now Fully Dynamic! ---
const StrikeTable = ({ data }) => {
  // Calculate CDF (cumulative probability) from PDF
  const calculateCDF = () => {
    const strikes = data.pdf.strikes;
    const pdfValues = data.pdf.values;
    const dx = strikes[1] - strikes[0]; // Strike spacing

    // Numerical integration to get CDF
    const cdf = [];
    let cumulative = 0;
    for (let i = 0; i < pdfValues.length; i++) {
      cumulative += pdfValues[i] * dx;
      cdf.push(cumulative);
    }

    return cdf;
  };

  const cdf = calculateCDF();
  const spot = data.spot_price;

  // Select 5 representative strikes around ATM
  const strikes = data.pdf.strikes;
  const atmIndex = strikes.findIndex(k => k >= spot);

  // Get strikes: 10% below, 5% below, ATM, 5% above, 10% above
  const selectedIndices = [
    Math.max(0, atmIndex - Math.floor(strikes.length * 0.15)),
    Math.max(0, atmIndex - Math.floor(strikes.length * 0.075)),
    atmIndex,
    Math.min(strikes.length - 1, atmIndex + Math.floor(strikes.length * 0.075)),
    Math.min(strikes.length - 1, atmIndex + Math.floor(strikes.length * 0.15))
  ];

  const tableData = selectedIndices.map((idx, i) => {
    const k = strikes[idx];
    const p_down = cdf[idx] * 100; // P(S < K)
    const p_up = (1 - cdf[idx]) * 100; // P(S > K)
    const dist = ((k - spot) / spot) * 100;
    const isAtm = i === 2; // Middle one is ATM

    return { k, p_down, p_up, dist, isAtm };
  });

  return (
    <motion.div
      className="glass-card rounded-2xl overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.2 }}
    >
      <div className="p-6 border-b border-white/5">
        <h3 className="font-bold text-lg">Strike Probability Matrix</h3>
        <p className="text-xs text-gray-400 mt-1">
          Cumulative probabilities derived from {data.ticker} option-implied PDF
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-surfaceHighlight/50 text-xs uppercase text-gray-500 tracking-wider">
              <th className="p-4 font-medium">Strike</th>
              <th className="p-4 font-medium">P(S &lt; K)</th>
              <th className="p-4 font-medium">P(S &gt; K)</th>
              <th className="p-4 font-medium">Distance</th>
            </tr>
          </thead>
          <tbody className="text-sm font-mono">
            {tableData.map((row, i) => (
              <motion.tr
                key={row.k}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.3 + i * 0.05 }}
                className={`border-b border-white/5 hover:bg-white/5 transition-colors ${row.isAtm ? 'bg-accent-cyan/5 border-l-2 border-l-accent-cyan' : ''}`}
              >
                <td className={`p-4 ${row.isAtm ? 'font-bold text-white' : 'text-gray-300'}`}>
                  ${row.k.toFixed(2)}
                  {row.isAtm && <span className="ml-2 text-xs text-accent-cyan">(ATM)</span>}
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-surfaceHighlight rounded-full overflow-hidden">
                      <div className="h-full bg-accent-red" style={{ width: `${Math.min(100, row.p_down)}%` }} />
                    </div>
                    <span className="text-gray-400">{row.p_down.toFixed(1)}%</span>
                  </div>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-surfaceHighlight rounded-full overflow-hidden">
                      <div className="h-full bg-accent-green" style={{ width: `${Math.min(100, row.p_up)}%` }} />
                    </div>
                    <span className="text-gray-400">{row.p_up.toFixed(1)}%</span>
                  </div>
                </td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs ${row.dist >= 0 ? 'bg-accent-green/10 text-accent-green' : 'bg-accent-red/10 text-accent-red'}`}>
                    {row.dist > 0 ? '+' : ''}{row.dist.toFixed(1)}%
                  </span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

// --- MAIN APP COMPONENT ---
export default function App() {
  const [ticker, setTicker] = useState("SPY");
  const [dte, setDte] = useState("30");
  const [mode, setMode] = useState("standard");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiData, setApiData] = useState(null);
  const [livePrice, setLivePrice] = useState(null);

  // Fetch live price when ticker changes
  useEffect(() => {
    const fetchLivePrice = async () => {
      if (!ticker) return;

      try {
        // Use our backend proxy endpoint to avoid CORS issues
        const response = await axios.get(`${API_URL}/api/chart/${ticker}`, {
          params: {
            interval: '1d',
            range: '1d'
          }
        });

        if (response.data.success && response.data.data.points && response.data.data.points.length > 0) {
          const points = response.data.data.points;
          const currentPrice = points[points.length - 1].price;
          const previousPrice = points.length > 1 ? points[points.length - 2].price : currentPrice;
          const change = currentPrice - previousPrice;
          const changePercent = (change / previousPrice) * 100;

          setLivePrice({
            price: currentPrice.toFixed(2),
            change: change,
            changePercent: changePercent.toFixed(2)
          });
        } else {
          setLivePrice({
            price: '---',
            change: 0,
            changePercent: '--'
          });
        }
      } catch (err) {
        console.error('Failed to fetch live price:', err);
        // Fallback to placeholder
        setLivePrice({
          price: '---',
          change: 0,
          changePercent: '--'
        });
      }
    };

    fetchLivePrice();
    // Refresh every 60 seconds
    const interval = setInterval(fetchLivePrice, 60000);
    return () => clearInterval(interval);
  }, [ticker]);

  const handleRunAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/analyze`, {
        ticker: ticker,
        days_to_expiry: parseInt(dte),
        analysis_mode: mode,
        use_sabr: true
      });

      if (response.data.success) {
        setApiData(response.data.data);
      } else {
        setError(response.data.error || 'Analysis failed');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to connect to backend API');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-primary font-sans text-white overflow-x-hidden selection:bg-accent-cyan/30">
      <MouseTracker />
      <ParticleBackground />

      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-primary/80 backdrop-blur-xl px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Zap className="text-accent-cyan" size={24} />
          <span className="font-bold tracking-tight text-lg">PDF<span className="text-gray-500">Viz</span></span>
        </div>
        <div className="flex gap-4 text-sm font-medium text-gray-400">
          <a href="#about" className="hover:text-white transition-colors">About</a>
        </div>
      </nav>

      <main className="container mx-auto px-4 relative z-10">
        <HeroSection ticker={ticker} livePrice={livePrice} />

        <InputControls
          onRunAnalysis={handleRunAnalysis}
          ticker={ticker}
          setTicker={setTicker}
          dte={dte}
          setDte={setDte}
          mode={mode}
          setMode={setMode}
          loading={loading}
        />

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto mb-8 px-4"
          >
            <div className="bg-accent-red/10 border border-accent-red/30 rounded-xl p-6 flex items-start gap-4">
              <AlertTriangle className="text-accent-red shrink-0" size={24} />
              <div>
                <h4 className="font-bold text-accent-red mb-2">Analysis Error</h4>
                <p className="text-sm text-gray-300">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="mt-3 text-xs bg-accent-red/20 hover:bg-accent-red/30 px-3 py-1 rounded-full transition-colors"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </motion.div>
        )}

        <AnimatePresence>
          {apiData && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                <div className="lg:col-span-2">
                  <MetricCards data={apiData} />
                  <PDFChart data={apiData} />
                </div>
                <div className="lg:col-span-1">
                  <div className="sticky top-24">
                     {/* Disclaimer */}
                    <div className="bg-surface/30 border border-accent-red/20 rounded-xl p-4 mb-6 flex items-start gap-3">
                        <AlertTriangle className="text-accent-red shrink-0" size={20} />
                        <div>
                            <h4 className="text-sm font-bold text-accent-red mb-1">Disclaimer</h4>
                            <p className="text-xs text-gray-400">Not financial advice. Distributions are estimates based on the Breeden-Litzenberger model. Past performance is not indicative of future results.</p>
                        </div>
                    </div>
                    <AIInsights data={apiData} />
                  </div>
                </div>
              </div>

              <StrikeTable data={apiData} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* About Section */}
      <section id="about" className="container mx-auto px-4 py-20 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto"
        >
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">About This Tool</h2>
            <p className="text-gray-400 text-lg">
              Learn how the Breeden-Litzenberger formula extracts risk-neutral probability distributions from option prices.
            </p>
          </div>

          <div className="glass-card rounded-3xl p-8 mb-8">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 rounded-xl bg-accent-cyan/10 border border-accent-cyan/20">
                <GraduationCap className="text-accent-cyan" size={24} />
              </div>
              <div>
                <h3 className="text-2xl font-bold mb-2">Educational Explainer Podcasts</h3>
                <p className="text-gray-400">
                  Deep dives into the mathematics and practical applications of option-implied probability density functions.
                </p>
              </div>
            </div>

            {/* Podcast Players */}
            <div className="space-y-6">
              {/* Short Version */}
              <div className="bg-surface/50 rounded-xl p-6 border border-white/5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-accent-green/10 flex items-center justify-center">
                    <span className="text-accent-green font-bold">11m</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-lg">Quick Overview</h4>
                    <p className="text-sm text-gray-400">Essential concepts in 11 minutes</p>
                  </div>
                </div>
                <audio
                  controls
                  className="w-full"
                  style={{
                    filter: 'invert(1) hue-rotate(180deg)',
                    height: '40px'
                  }}
                >
                  <source src="/podcast-short.m4a" type="audio/mp4" />
                  Your browser does not support the audio element.
                </audio>
              </div>

              {/* Long Version */}
              <div className="bg-surface/50 rounded-xl p-6 border border-white/5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-accent-purple/10 flex items-center justify-center">
                    <span className="text-accent-purple font-bold">33m</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-lg">Comprehensive Deep Dive</h4>
                    <p className="text-sm text-gray-400">Complete mathematical treatment and applications</p>
                  </div>
                </div>
                <audio
                  controls
                  className="w-full"
                  style={{
                    filter: 'invert(1) hue-rotate(180deg)',
                    height: '40px'
                  }}
                >
                  <source src="/podcast-long.m4a" type="audio/mp4" />
                  Your browser does not support the audio element.
                </audio>
              </div>
            </div>
          </div>

          {/* Technical Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card rounded-2xl p-6">
              <h4 className="font-bold text-lg mb-3 flex items-center gap-2">
                <Activity className="text-accent-cyan" size={20} />
                Key Features
              </h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-accent-green mt-0.5">•</span>
                  Real-time option chain analysis
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-green mt-0.5">•</span>
                  SABR volatility surface modeling
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-green mt-0.5">•</span>
                  Risk-neutral PDF extraction
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-green mt-0.5">•</span>
                  AI-powered market sentiment analysis
                </li>
              </ul>
            </div>

            <div className="glass-card rounded-2xl p-6">
              <h4 className="font-bold text-lg mb-3 flex items-center gap-2">
                <Shield className="text-accent-green" size={20} />
                Methodology
              </h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-accent-cyan mt-0.5">•</span>
                  Breeden-Litzenberger formula (1978)
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-cyan mt-0.5">•</span>
                  Cubic spline interpolation
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-cyan mt-0.5">•</span>
                  No-arbitrage constraints
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-cyan mt-0.5">•</span>
                  Statistical moment calculation
                </li>
              </ul>
            </div>
          </div>
        </motion.div>
      </section>

      <footer className="border-t border-white/5 mt-12 py-12 text-center text-gray-600 text-sm z-10 relative bg-primary">
        <div className="flex justify-center gap-6 mb-8">
          <GraduationCap size={20} className="hover:text-accent-cyan transition-colors cursor-pointer" />
          <Shield size={20} className="hover:text-accent-green transition-colors cursor-pointer" />
        </div>
        <p>&copy; 2025 Option-Implied PDF Visualizer. All rights reserved.</p>
      </footer>
    </div>
  );
}
