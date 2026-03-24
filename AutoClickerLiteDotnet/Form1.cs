using System.Drawing.Drawing2D;
using System.Runtime.InteropServices;

namespace AutoClickerLiteDotnet;

/// <summary>WinForms panel with CTk-like rounded rectangle fill (corner_radius ~ 10).</summary>
internal sealed class RoundedCardPanel : Panel
{
    public int CornerRadius { get; set; } = 10;

    /// <summary>Interior fill color (rounded surface). <see cref="Control.BackColor"/> is the outer/hole color.</summary>
    public Color FaceColor { get; set; } = Color.FromArgb(30, 35, 41);

    public RoundedCardPanel()
    {
        SetStyle(
            ControlStyles.AllPaintingInWmPaint
                | ControlStyles.OptimizedDoubleBuffer
                | ControlStyles.UserPaint
                | ControlStyles.ResizeRedraw,
            true);
        UpdateStyles();
        // Must match the visible "hole" (form background). WinForms may erase/fill the client
        // rectangle with BackColor before OnPaint; if this equals the card face color, corners stay square.
        BackColor = Color.FromArgb(23, 26, 33);
    }

    protected override void OnParentChanged(EventArgs e)
    {
        base.OnParentChanged(e);
        if (Parent != null)
        {
            BackColor = Parent.BackColor;
        }

        Invalidate();
    }

    protected override void OnPaintBackground(PaintEventArgs pevent)
    {
    }

    protected override void OnSizeChanged(EventArgs e)
    {
        base.OnSizeChanged(e);
        ApplyClipRegion();
    }

    protected override void OnParentBackColorChanged(EventArgs e)
    {
        base.OnParentBackColorChanged(e);
        Invalidate();
    }

    private void ApplyClipRegion()
    {
        if (Width < 4 || Height < 4)
        {
            return;
        }

        var inset = ClientRectangle;
        inset.Inflate(-1, -1);
        using var path = CreateRoundedPath(inset, CornerRadius);
        Region = new Region(path);
    }

    protected override void OnPaint(PaintEventArgs e)
    {
        var g = e.Graphics;
        g.SmoothingMode = SmoothingMode.AntiAlias;

        var clear = Parent?.BackColor ?? SystemColors.Control;
        using (var bg = new SolidBrush(clear))
        {
            g.FillRectangle(bg, ClientRectangle);
        }

        var inset = ClientRectangle;
        inset.Inflate(-1, -1);
        using var path = CreateRoundedPath(inset, CornerRadius);
        using var fill = new SolidBrush(FaceColor);
        g.FillPath(fill, path);
    }

    private static GraphicsPath CreateRoundedPath(Rectangle bounds, int radius)
    {
        int d = Math.Min(radius * 2, Math.Min(bounds.Width, bounds.Height));
        if (d < 2)
        {
            d = 2;
        }

        var path = new GraphicsPath();
        path.AddArc(bounds.Left, bounds.Top, d, d, 180, 90);
        path.AddArc(bounds.Right - d, bounds.Top, d, d, 270, 90);
        path.AddArc(bounds.Right - d, bounds.Bottom - d, d, d, 0, 90);
        path.AddArc(bounds.Left, bounds.Bottom - d, d, d, 90, 90);
        path.CloseFigure();
        return path;
    }

}

/// <summary>Circular status lamp (no square Panel background).</summary>
internal sealed class StatusIndicatorDot : Control
{
    public StatusIndicatorDot()
    {
        SetStyle(
            ControlStyles.AllPaintingInWmPaint
                | ControlStyles.OptimizedDoubleBuffer
                | ControlStyles.UserPaint
                | ControlStyles.ResizeRedraw,
            true);
        UpdateStyles();
        TabStop = false;
        Size = new Size(12, 12);
    }

    protected override void OnPaintBackground(PaintEventArgs pevent)
    {
    }

    protected override void OnSizeChanged(EventArgs e)
    {
        base.OnSizeChanged(e);
        if (Width < 2 || Height < 2)
        {
            return;
        }

        const float pad = 0.5f;
        using var path = new GraphicsPath();
        path.AddEllipse(pad, pad, Width - 2 * pad, Height - 2 * pad);
        Region = new Region(path);
    }

    protected override void OnPaint(PaintEventArgs e)
    {
        var g = e.Graphics;
        g.SmoothingMode = SmoothingMode.AntiAlias;
        g.PixelOffsetMode = PixelOffsetMode.HighQuality;
        const float pad = 0.5f;
        using var b = new SolidBrush(BackColor);
        g.FillEllipse(b, pad, pad, Width - 2 * pad, Height - 2 * pad);
    }
}

public sealed class Form1 : Form
{
    private const int WM_HOTKEY = 0x0312;
    private const int HOTKEY_START = 1;
    private const int HOTKEY_STOP = 2;
    private const int HOTKEY_EXIT = 3;
    private const uint MOD_CONTROL = 0x0002;
    private const uint MOD_SHIFT = 0x0004;

    private static readonly Color Bg = Color.FromArgb(23, 26, 33);
    private static readonly Color Card = Color.FromArgb(30, 35, 41);
    private static readonly Color Accent = Color.FromArgb(26, 159, 255);
    private static readonly Color IdleDot = Color.FromArgb(232, 168, 73);
    private static readonly Color BlockedDot = Color.FromArgb(216, 87, 78);
    private static readonly Color RunningDot = Color.FromArgb(94, 164, 84);

    [StructLayout(LayoutKind.Sequential)]
    private struct INPUT
    {
        public uint type;
        public MOUSEINPUT mi;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct MOUSEINPUT
    {
        public int dx;
        public int dy;
        public uint mouseData;
        public uint dwFlags;
        public uint time;
        public nint dwExtraInfo;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [DllImport("user32.dll")] private static extern bool RegisterHotKey(nint hWnd, int id, uint fsModifiers, uint vk);
    [DllImport("user32.dll")] private static extern bool UnregisterHotKey(nint hWnd, int id);
    [DllImport("user32.dll")] private static extern bool GetCursorPos(out Point pt);
    [DllImport("user32.dll")] private static extern bool GetWindowRect(nint hWnd, out RECT rect);
    [DllImport("user32.dll")] private static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

    private readonly TextBox _intervalBox = new();
    private readonly TextBox _jitterBox = new();
    private readonly Label _statusWord = new();
    private readonly StatusIndicatorDot _statusDot = new();
    private readonly System.Windows.Forms.Timer _statusTimer = new() { Interval = 120 };
    private readonly Random _rng = new();

    private Thread? _worker;
    private volatile bool _running;
    private volatile int _intervalMs = 100;
    private volatile int _jitterMs;
    private bool _closing;
    private Point _dragStart;

    public Form1()
    {
        SuspendLayout();

        FormBorderStyle = FormBorderStyle.None;
        StartPosition = FormStartPosition.CenterScreen;
        TopMost = true;
        BackColor = Bg;
        ClientSize = new Size(292, 364);
        MinimumSize = new Size(260, 310);
        Text = "Auto Clicker";
        Font = new Font("Segoe UI", 10f);
        // Borderless forms do not pick up the .exe icon for the taskbar; use the embedded PE icon.
        ShowIcon = true;
        try
        {
            var ico = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            if (ico is not null)
            {
                Icon = ico;
            }
        }
        catch
        {
        }

        BuildUi();

        _statusTimer.Tick += (_, _) => UpdateStatus();
        _statusTimer.Start();

        Shown += (_, _) =>
        {
            RegisterHotKey(Handle, HOTKEY_START, 0, (uint)Keys.F6);
            RegisterHotKey(Handle, HOTKEY_STOP, 0, (uint)Keys.F7);
            RegisterHotKey(Handle, HOTKEY_EXIT, MOD_CONTROL | MOD_SHIFT, (uint)Keys.E);
            _worker = new Thread(ClickLoop) { IsBackground = true, Name = "clicker" };
            _worker.Start();
        };

        FormClosed += (_, _) =>
        {
            _running = false;
            _statusTimer.Stop();
            UnregisterHotKey(Handle, HOTKEY_START);
            UnregisterHotKey(Handle, HOTKEY_STOP);
            UnregisterHotKey(Handle, HOTKEY_EXIT);
        };

        ResumeLayout(false);
    }

    private void BuildUi()
    {
        var titleBar = new Panel
        {
            Location = new Point(0, 0),
            Size = new Size(ClientSize.Width, 38),
            BackColor = Card,
            Anchor = AnchorStyles.Left | AnchorStyles.Top | AnchorStyles.Right,
        };

        var titleLabel = new Label
        {
            Text = "Auto Clicker",
            ForeColor = Accent,
            Font = new Font("Segoe UI", 13f, FontStyle.Bold),
            Location = new Point(10, 8),
            AutoSize = true,
            BackColor = Color.Transparent,
        };

        var minButton = MakeChromeButton("_");
        minButton.Location = new Point(ClientSize.Width - 62, 7);
        minButton.Anchor = AnchorStyles.Top | AnchorStyles.Right;
        minButton.Click += (_, _) => WindowState = FormWindowState.Minimized;

        var closeButton = MakeChromeButton("X");
        closeButton.Location = new Point(ClientSize.Width - 32, 7);
        closeButton.Anchor = AnchorStyles.Top | AnchorStyles.Right;
        closeButton.Click += (_, _) => Close();

        titleBar.Controls.Add(titleLabel);
        titleBar.Controls.Add(minButton);
        titleBar.Controls.Add(closeButton);

        titleBar.MouseDown += BeginDrag;
        titleBar.MouseMove += DoDrag;
        titleLabel.MouseDown += BeginDrag;
        titleLabel.MouseMove += DoDrag;

        var cardWidth = ClientSize.Width - 20;
        var timingCard = MakeCard(new Rectangle(10, 44, cardWidth, 130));
        timingCard.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
        var hotkeysCard = MakeCard(new Rectangle(10, 178, cardWidth, 116));
        hotkeysCard.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
        var statusCard = MakeCard(new Rectangle(10, 298, cardWidth, 58));
        statusCard.Anchor = AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom;

        BuildTimingSection(timingCard);
        BuildHotkeysSection(hotkeysCard);
        BuildStatusSection(statusCard);

        Controls.Add(titleBar);
        Controls.Add(timingCard);
        Controls.Add(hotkeysCard);
        Controls.Add(statusCard);
    }

    private void BuildTimingSection(Control parent)
    {
        parent.Controls.Add(MakeSectionHeader("Timing", 10, 8));

        parent.Controls.Add(MakeMuted("Interval (ms)", 10, 34));
        ConfigureInput(_intervalBox, "100", new Point(120, 31));
        parent.Controls.Add(_intervalBox);

        parent.Controls.Add(MakeMuted("Jitter max (ms)", 10, 60));
        ConfigureInput(_jitterBox, "0", new Point(120, 57));
        parent.Controls.Add(_jitterBox);

        var applyBtn = new Button
        {
            Text = "Apply",
            Location = new Point(10, 88),
            Size = new Size(78, 23),
            BackColor = Color.FromArgb(42, 71, 94),
            ForeColor = Color.FromArgb(229, 238, 245),
            FlatStyle = FlatStyle.Flat,
            Font = new Font("Segoe UI", 9f, FontStyle.Regular),
            TabStop = false,
            UseCompatibleTextRendering = false,
        };
        applyBtn.FlatAppearance.BorderSize = 0;
        applyBtn.Click += (_, _) => ApplyTiming();
        parent.Controls.Add(applyBtn);
    }

    private void BuildHotkeysSection(Control parent)
    {
        parent.Controls.Add(MakeSectionHeader("Global hotkeys", 10, 10));
        AddHotkeyRow(parent, "Start clicking", "f6", 42);
        AddHotkeyRow(parent, "Stop clicking", "f7", 64);
        AddHotkeyRow(parent, "Exit app", "ctrl + shift + e", 86);
    }

    private void BuildStatusSection(Control parent)
    {
        parent.Controls.Add(MakeSectionHeader("Status", 10, 6));

        _statusDot.Location = new Point(10, 32);
        _statusDot.Size = new Size(12, 12);
        _statusDot.BackColor = IdleDot;

        _statusWord.Text = "Idle";
        _statusWord.ForeColor = Color.FromArgb(229, 238, 245);
        _statusWord.Font = new Font("Segoe UI", 11f, FontStyle.Bold);
        _statusWord.Location = new Point(30, 28);
        _statusWord.AutoSize = true;
        _statusWord.BackColor = Color.Transparent;

        parent.Controls.Add(_statusDot);
        parent.Controls.Add(_statusWord);
    }

    private static RoundedCardPanel MakeCard(Rectangle bounds)
    {
        return new RoundedCardPanel
        {
            Location = bounds.Location,
            Size = bounds.Size,
            BackColor = Bg,
            FaceColor = Card,
            CornerRadius = 10,
        };
    }

    private static Label MakeSectionHeader(string text, int x, int y)
    {
        return new Label
        {
            Text = text,
            Location = new Point(x, y),
            AutoSize = true,
            ForeColor = Color.FromArgb(199, 213, 224),
            Font = new Font("Segoe UI", 11f, FontStyle.Bold),
            BackColor = Color.Transparent,
        };
    }

    private static Label MakeMuted(string text, int x, int y)
    {
        return new Label
        {
            Text = text,
            Location = new Point(x, y),
            AutoSize = true,
            ForeColor = Color.FromArgb(143, 152, 160),
            Font = new Font("Segoe UI", 10f),
            BackColor = Color.Transparent,
        };
    }

    private static Button MakeChromeButton(string text)
    {
        var btn = new Button
        {
            Text = text,
            Size = new Size(26, 22),
            FlatStyle = FlatStyle.Flat,
            BackColor = Color.FromArgb(42, 47, 58),
            ForeColor = Color.FromArgb(229, 238, 245),
            Font = new Font("Segoe UI", 9f, FontStyle.Bold),
            TabStop = false,
        };
        btn.FlatAppearance.BorderSize = 0;
        return btn;
    }

    private static void ConfigureInput(TextBox box, string value, Point location)
    {
        box.Text = value;
        box.Location = location;
        box.Size = new Size(70, 24);
        box.BorderStyle = BorderStyle.FixedSingle;
        box.BackColor = Color.FromArgb(51, 56, 62);
        box.ForeColor = Color.FromArgb(229, 238, 245);
        box.Font = new Font("Consolas", 10f);
    }

    private static void AddHotkeyRow(Control parent, string left, string right, int y)
    {
        parent.Controls.Add(MakeMuted(left, 10, y));
        parent.Controls.Add(new Label
        {
            Text = right,
            Location = new Point(120, y),
            AutoSize = true,
            ForeColor = Color.FromArgb(229, 238, 245),
            Font = new Font("Consolas", 10f, FontStyle.Bold),
            BackColor = Color.Transparent,
        });
    }

    private void BeginDrag(object? sender, MouseEventArgs e)
    {
        if (e.Button == MouseButtons.Left)
        {
            _dragStart = e.Location;
        }
    }

    private void DoDrag(object? sender, MouseEventArgs e)
    {
        if (e.Button == MouseButtons.Left)
        {
            Left += e.X - _dragStart.X;
            Top += e.Y - _dragStart.Y;
        }
    }

    private void ApplyTiming()
    {
        if (!int.TryParse(_intervalBox.Text.Trim(), out var interval))
        {
            interval = 100;
        }
        if (!int.TryParse(_jitterBox.Text.Trim(), out var jitter))
        {
            jitter = 0;
        }

        _intervalMs = Math.Max(1, interval);
        _jitterMs = Math.Max(0, jitter);
    }

    private void UpdateStatus()
    {
        if (!_running)
        {
            _statusWord.Text = "Idle";
            _statusDot.BackColor = IdleDot;
        }
        else if (CursorOverSelf())
        {
            _statusWord.Text = "Blocked";
            _statusDot.BackColor = BlockedDot;
        }
        else
        {
            _statusWord.Text = "Running";
            _statusDot.BackColor = RunningDot;
        }
        _statusDot.Invalidate();
    }

    private bool CursorOverSelf()
    {
        if (!GetCursorPos(out var p))
        {
            return false;
        }
        if (!GetWindowRect(Handle, out var r))
        {
            return false;
        }
        return p.X >= r.Left && p.X < r.Right && p.Y >= r.Top && p.Y < r.Bottom;
    }

    private void ClickLoop()
    {
        var down = new INPUT { type = 0, mi = new MOUSEINPUT { dwFlags = 0x0002 } };
        var up = new INPUT { type = 0, mi = new MOUSEINPUT { dwFlags = 0x0004 } };

        while (!_closing)
        {
            if (!_running)
            {
                Thread.Sleep(50);
                continue;
            }

            if (CursorOverSelf())
            {
                Thread.Sleep(20);
                continue;
            }

            SendInput(1, new[] { down }, Marshal.SizeOf<INPUT>());
            SendInput(1, new[] { up }, Marshal.SizeOf<INPUT>());

            var extra = _jitterMs > 0 ? _rng.Next(0, _jitterMs + 1) : 0;
            var delay = Math.Max(1, _intervalMs + extra);
            Thread.Sleep(delay);
        }
    }

    protected override void WndProc(ref Message m)
    {
        if (m.Msg == WM_HOTKEY)
        {
            var id = (int)m.WParam;
            if (id == HOTKEY_START)
            {
                ApplyTiming();
                _running = true;
            }
            else if (id == HOTKEY_STOP)
            {
                _running = false;
            }
            else if (id == HOTKEY_EXIT)
            {
                Close();
            }
        }

        base.WndProc(ref m);
    }

    protected override void OnFormClosing(FormClosingEventArgs e)
    {
        _closing = true;
        _running = false;
        base.OnFormClosing(e);
    }
}
