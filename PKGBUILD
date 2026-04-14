pkgname=hyprcat
pkgver=r5.g9931aed
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
provides=('hyprcat')
conflicts=('hyprcat-git')
source=("git+$url.git")
sha256sums=('SKIP')

_source_dir() {
  if [[ -f "$startdir/bin/hyprcat-session" && -f "$startdir/main.py" && -d "$startdir/config" ]]; then
    printf '%s\n' "$startdir"
  else
    printf '%s\n' "$srcdir/Cat-Hypr-Rice"
  fi
}

pkgver() {
  local source_dir
  source_dir="$(_source_dir)"
  cd "$source_dir"
  printf 'r%s.g%s' "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
  local source_dir
  source_dir="$(_source_dir)"
  cd "$source_dir"

  install -d "$pkgdir/usr/bin"
  install -d "$pkgdir/usr/share/applications"
  install -d "$pkgdir/usr/share/doc/hyprcat"
  install -d "$pkgdir/usr/share/hyprcat"
  install -d "$pkgdir/usr/share/wayland-sessions"

  cp -r config "$pkgdir/usr/share/hyprcat/"
  cp -r scripts "$pkgdir/usr/share/hyprcat/"
  cp -r wallpapers "$pkgdir/usr/share/hyprcat/"

  install -m755 main.py "$pkgdir/usr/share/hyprcat/settings_app.py"
  install -m755 bin/hyprcat-session "$pkgdir/usr/bin/hyprcat-session"
  install -m755 bin/hyprcat-settings "$pkgdir/usr/bin/hyprcat-settings"
  install -m644 packaging/hyprcat.desktop "$pkgdir/usr/share/wayland-sessions/hyprcat.desktop"
  install -m644 packaging/hyprcat-settings.desktop "$pkgdir/usr/share/applications/hyprcat-settings.desktop"
  install -m644 README.md "$pkgdir/usr/share/doc/hyprcat/README.md"
}
