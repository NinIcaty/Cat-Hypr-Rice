pkgname=pyprland-desktop-git
pkgver=r3.gcc18c30
pkgrel=1
pkgdesc="Material 3 inspired standalone Hyprland desktop session with a settings app"
arch=('x86_64')
url='https://github.com/NinIcaty/Cat-Hypr-Rice'
license=('custom')
depends=(
  'gtk3'
  'hyprland'
  'hyprpaper'
  'libnotify'
  'playerctl'
  'python'
  'python-gobject'
  'rofi'
  'swaync'
  'waybar'
)
makedepends=('git')
optdepends=(
  'anyrun: preferred app launcher'
  'brightnessctl: brightness shortcuts'
  'ghostty: default terminal command'
  'hyprlock: lock screen integration'
  'hyprshot: screenshot shortcuts'
  'nautilus: default file manager command'
  'ttf-jetbrains-mono-nerd: recommended font'
)
provides=('pyprland-desktop')
conflicts=('pyprland-desktop')
source=("git+$url.git")
sha256sums=('SKIP')

pkgver() {
  cd "$srcdir/Cat-Hypr-Rice"
  printf 'r%s.g%s' "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
  cd "$srcdir/Cat-Hypr-Rice"

  install -d "$pkgdir/usr/bin"
  install -d "$pkgdir/usr/share/applications"
  install -d "$pkgdir/usr/share/doc/pyprland-desktop"
  install -d "$pkgdir/usr/share/pyprland-desktop"
  install -d "$pkgdir/usr/share/wayland-sessions"

  cp -r config "$pkgdir/usr/share/pyprland-desktop/"
  cp -r scripts "$pkgdir/usr/share/pyprland-desktop/"
  cp -r wallpapers "$pkgdir/usr/share/pyprland-desktop/"

  install -m755 main.py "$pkgdir/usr/share/pyprland-desktop/settings_app.py"
  install -m755 bin/pyprland-session "$pkgdir/usr/bin/pyprland-session"
  install -m755 bin/pyprland-settings "$pkgdir/usr/bin/pyprland-settings"
  install -m644 packaging/pyprland.desktop "$pkgdir/usr/share/wayland-sessions/pyprland.desktop"
  install -m644 packaging/pyprland-settings.desktop "$pkgdir/usr/share/applications/pyprland-settings.desktop"
  install -m644 README.md "$pkgdir/usr/share/doc/pyprland-desktop/README.md"
}
