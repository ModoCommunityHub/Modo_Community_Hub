from typing import List
from pathlib import Path

try:
    from PySide6.QtGui import QCursor, QDesktopServices, QMouseEvent
    from PySide6.QtGui import QPixmap, QIcon, QPalette, QColor, QPainter
    from PySide6.QtCore import Qt, QUrl, QRect, QTimer, QThread
    from PySide6.QtCore import QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation
    from PySide6.QtWidgets import (
        QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QToolButton, QScrollArea,
        QPlainTextEdit, QSizePolicy, QFrame, QTabWidget, QLineEdit, QTabBar, QStylePainter,
        QStyleOptionTab, QStyle
    )
except ImportError:
    # Fallback to PySide2 if PySide6 is not available
    from PySide2.QtGui import QCursor, QDesktopServices, QMouseEvent
    from PySide2.QtGui import QPixmap, QIcon, QPalette, QColor, QPainter
    from PySide2.QtCore import Qt, QUrl, QRect, QTimer, QThread
    from PySide2.QtCore import QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation
    from PySide2.QtWidgets import (
        QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QToolButton, QScrollArea,
        QPlainTextEdit, QSizePolicy, QFrame, QTabWidget, QLineEdit, QTabBar, QStylePainter,
        QStyleOptionTab, QStyle
    )

from .prefs import Text, Paths, DATA, KitData, AuthorData
from .database import search_kits, get_author, get_kits, get_author_kits
from .github import DatabaseWorker, AvatarWorker

class KitWidget(QWidget):
    """Class to display the information of a given kit."""

    def __init__(self, kit_data: KitData, show_author: bool = True) -> None:
        """Class to display the kit information in the main UI.

        Args:
            kit_data: The kit data from the database.
            show_author: Whether to show the author information. Default is True.
        """
        super(KitWidget, self).__init__()
        self.kit_data = kit_data
        self.show_author = show_author
        self._build_ui()
        self._connect_ui()

    def _build_ui(self) -> None:
        """Builds the UI for the kit widget."""
        self.setContentsMargins(0, 0, 0, 0)
        self.base_layout = QVBoxLayout()
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.base_layout)
        self.lbl_author = QLabel(f"Author: {self.kit_data.author}")

        self.description = QPlainTextEdit(self.kit_data.description)
        self.description.setObjectName("description")
        self.description.setReadOnly(True)
        self.description.setMaximumHeight(120)
        self.description.setMinimumHeight(40)

        self.btn_link = Button("View")
        self.url_view = QUrl(self.kit_data.url)

        self.btn_install = Button("Install")

        self.btn_help = Button("Help")
        self.url_help = QUrl(self.kit_data.help)

        # Create the layout to hold the interactive buttons
        self.interactive_layout = QHBoxLayout()
        self.interactive_layout.setContentsMargins(0, 0, 0, 0)
        self.interactive_layout.addWidget(self.btn_link)
        self.interactive_layout.addWidget(self.btn_install)
        self.interactive_layout.addWidget(self.btn_help)

        # Check if banner is available and add it to the widget.
        self._add_banner()
        # Add all elements to the base layout.
        self.base_layout.addWidget(self.description)
        self.base_layout.addLayout(self.interactive_layout)
        # Add author information if needed.
        if self.show_author:
            self.base_layout.addWidget(self.lbl_author)
            self.lbl_author.setText(
                Text.author.format(self.kit_data.author, self.kit_data.author))
            self.lbl_author.mousePressEvent = self.open_author
        # Check if the kit is installable.
        if self.kit_data.installable:
            installed_kit = DATA.modo_kits.get(self.kit_data.name, False)
            if not installed_kit:
                self.btn_install.setText("Install")
            elif installed_kit and installed_kit.version != self.kit_data.version:
                self.btn_install.setText(
                    f"Update! v{installed_kit.version} -> {self.kit_data.version}"
                )
                self.btn_install.setProperty('update', True)
            else:
                self.btn_install.setText("Installed")
                self.btn_install.setDisabled(True)

    def _handle_installed_kit(self) -> None:
        ...

    def set_height(self) -> None:
        """Sets the height of the description to fit the content."""
        # Calculate the total height of all blocks (lines) in the document
        self.description.document().setTextWidth(self.description.viewport().width())
        self.description.document().adjustSize()

        # Calculate the total height of the content
        layout = self.description.document().documentLayout()
        content_height = layout.documentSize().height()

        # Add the top and bottom margins
        content_height += self.description.contentsMargins().top() + self.description.contentsMargins().bottom()
        # Apply the calculated height, ensuring it does not exceed the maximum height
        self.description.setFixedHeight(min(content_height, self.description.maximumHeight()))

    def _add_banner(self) -> None:
        """Adds a banner to the widget if it exists."""
        banner_image = Paths.BANNERS / f"{self.kit_data.name}.png"
        if banner_image.exists():
            self.banner = Banner(image=banner_image)
            self.base_layout.addWidget(self.banner)

    def _connect_ui(self) -> None:
        """Connects the UI elements to their respective functions."""
        self.btn_link.clicked.connect(lambda: QDesktopServices.openUrl(self.url_view))
        self.btn_help.clicked.connect(lambda: QDesktopServices.openUrl(self.url_help))

    def open_author(self, event: QMouseEvent) -> None:
        """Opens the author tab when the author's name is clicked.

        Args:
            event: The mouse click event.
        """
        # Get the tab widget
        tab_widget: QTabWidget = DATA.mkc_window.tabs
        # Find if Author is already a tab
        author_widget = tab_widget.findChild(QScrollArea, self.kit_data.author)
        if not author_widget:
            author_data = get_author(self.kit_data.author)
            # Create new avatar tab
            author_widget = AuthorTab(author_data)
            tab_widget.addTab(author_widget, self.kit_data.author)
        # Set the tab as active
        tab_widget.setCurrentIndex(tab_widget.indexOf(author_widget))


class Button(QPushButton):
    """Class to format all buttons alike."""

    def __init__(self, text: str = "Button", icon: QIcon = None) -> None:
        """Inherited Pushbutton class to format all buttons alike.

        Args:
            text: The text to display on the button.
            icon: The icon to display on the button.
        """
        super(Button, self).__init__(text)
        # Add icon if given one.
        if icon:
            self.setIcon(icon)
        # Enable the pointer mouse.
        self.setCursor(QCursor(Qt.PointingHandCursor))


class Banner(QLabel):
    """Class to display a banner image."""

    def __init__(self, image: Path, parent: QWidget = None) -> None:
        """Banner class to display a Kit banner.

        Args:
            image: The image to display as the banner.
            parent: The parent widget.
        """
        super(Banner, self).__init__(parent)
        self.setAlignment(Qt.AlignLeft)
        self.setContentsMargins(0, 0, 0, 0)
        self.setPixmap(QPixmap(image.as_posix()))
        # Remove padding for pixmap
        self.setScaledContents(True)


class FoldContainer(QWidget):
    """Class to create a collapsable container for the kit widgets."""

    def __init__(self, name: str = "test", version: str = None, parent: QWidget = None) -> None:
        """Initialization of the FoldContainer class.

        Args:
            name: The name of the container.
            version: The version of the kit.
            parent: The parent widget.
        """
        super(FoldContainer, self).__init__(parent)
        self.setObjectName(name)
        self.layout = QVBoxLayout()
        self.anim_length = 200
        self.collapsed_height = 0
        self.forward = QAbstractAnimation.Forward
        self.reverse = QAbstractAnimation.Backward
        button_text = f"{name} v{version}" if version else name
        self.toggle_button = QToolButton(text=button_text, checkable=True, checked=False)
        self.toggle_animation = QParallelAnimationGroup(self)
        self.content_area = QScrollArea(maximumHeight=0, minimumHeight=0)
        self.content = None
        self.build_ui()

    def build_ui(self) -> None:
        """Builds the UI"""
        self.setContentsMargins(0, 0, 0, 0)
        self.toggle_button.setFixedHeight(20)
        self.toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        # Enable the pointer mouse.
        self.toggle_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_button.pressed.connect(self.on_pressed)

        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_area.setFrameShape(QFrame.NoFrame)

        container_layout = QVBoxLayout(self)
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.toggle_button)
        container_layout.addWidget(self.content_area)
        # Add animations for smooth opening
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self.content_area, b"maximumHeight"))

    def on_pressed(self) -> None:
        """Enable animation when user selects the bar."""
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(Qt.DownArrow if not checked else Qt.RightArrow)
        self.toggle_animation.setDirection(self.forward if not checked else self.reverse)
        self.toggle_animation.start()

    def expand(self, value: int) -> None:
        """Expands the content to fit more stuff.

        Args:
            value: The height value to expand the content by.
        """
        content_height = self.layout.sizeHint().height() + value
        # Initialize all added animations with the same values.
        self.animation_setup(content_height)
        self.toggle_animation.start()

    def set_content(self, content: QWidget) -> None:
        """Sets a widget as the containers displayable content.

        Args:
            content: The widget to set as the core content.
        """
        self.content = content
        # Add content to layout
        self.layout.addWidget(self.content)
        # Set layout as the main content layout
        self.content_area.setLayout(self.layout)
        # Calculate the height of the widget when closed.
        self.collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        # Get the current height of the new layout with added content
        content_height = self.layout.sizeHint().height()
        self.animation_setup(content_height)

    def animation_setup(self, height: int) -> None:
        """Sets up the animations for the container for a smooth open/close.

        Args:
            height: The height to animate to.
        """
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(self.anim_length)
            animation.setStartValue(self.collapsed_height)
            animation.setEndValue(self.collapsed_height + height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(self.anim_length)
        content_animation.setStartValue(0)
        content_animation.setEndValue(height)


class KitSearchBar(QWidget):
    """Custom search bar for the kits tab."""

    def __init__(self, kit_tab: 'KitsTab', parent: QWidget = None):
        """Initialization of the search bar for the kits tab.

        Args:
            kit_tab: Widget to search children for.
            parent: Parent to attach widget to.
        """
        super(KitSearchBar, self).__init__(parent)
        self.kit_tab = kit_tab

        # Build the UI
        self._build_ui()

    def _build_ui(self) -> None:
        """Builds the UI for the search bar."""
        self.base_layout = QHBoxLayout()
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.base_layout)
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("kit_search")
        self.search_bar.setPlaceholderText("Search...")
        # Set placeholder property for css.
        self.search_bar.setProperty("placeholder", True)

        self.base_layout.addWidget(self.search_bar)
        # Connect search bar to search function.
        self.search_bar.textChanged.connect(self.search)

    def search(self, text: str) -> None:
        """Handles searching the widgets and disabling the ones that do not match.

        Args:
            text: The search text.
        """
        if not text:
            self.search_bar.setProperty("placeholder", True)
        else:
            self.search_bar.setProperty("placeholder", False)

        self.search_bar.style().polish(self.search_bar)

        # Get id of all matching kits
        kit_ids = search_kits(text)

        for kit_id, kit in enumerate(self.kit_tab.kits):
            if kit_id in kit_ids:
                kit.setVisible(True)
            else:
                kit.setVisible(False)


class KitsTab(QWidget):
    """Class to display the kits in the main UI."""

    def __init__(self, parent: QWidget = None) -> None:
        """Scroll area that populates with incoming kit information.

        Args:
            parent: Widget to set as parent.
        """
        super(KitsTab, self).__init__(parent)
        self.kits: List[FoldContainer] = []
        self._ui_setup()
        self._sync_database()

    def _ui_setup(self) -> None:
        """Sets up the UI for the kit tab."""
        self.setContentsMargins(4, 4, 4, 4)
        # Search
        self.search_bar = KitSearchBar(self)
        # Base layout for the tab
        self.base_widget = QWidget()
        self.base_layout = QVBoxLayout()
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setAlignment(Qt.AlignTop)
        self.base_layout.addWidget(self.search_bar)
        self.base_widget.setLayout(self.base_layout)
        # Scroll area for kits
        self.kits_widget = QWidget()
        self.kits_scroll = QScrollArea()
        self.kits_scroll.setContentsMargins(0, 0, 0, 0)
        self.kits_scroll.setWidget(self.kits_widget)
        self.kits_scroll.setWidgetResizable(True)
        self.kits_layout = QVBoxLayout()
        self.kits_layout.setContentsMargins(0, 0, 0, 0)
        self.kits_layout.setAlignment(Qt.AlignTop)
        self.kits_scroll.setWidget(self.kits_widget)
        self.kits_widget.setLayout(self.kits_layout)
        # Add Kits to the base layout
        self.base_layout.addWidget(self.kits_scroll)
        # Set the base layout as the main layout
        self.setLayout(self.base_layout)

    def _sync_database(self) -> None:
        """Spawns a thread to handle pulling the latest kit database."""
        self.thread = QThread()
        self.worker = DatabaseWorker()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.on_finished)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_finished(self) -> None:
        """Handles the completion of the database worker."""
        self.thread.quit()
        self.thread.wait()
        self._add_kits()

    def on_error(self, error: str) -> None:
        """Handles the error from the database worker.

        Args:
            error: The error raised by the worker.
        """
        print(f"Error: {error}")
        self.thread.quit()
        self.thread.wait()

    def _add_kits(self) -> None:
        """Iterate over the kits database table and add the kits to the UI."""
        for kit_data in get_kits():
            # Generate a collapsable container
            kit_container = FoldContainer(name=kit_data.label, version=kit_data.version)
            kit_container.set_content(KitWidget(kit_data))
            self.kits.append(kit_container)
            self.kits_layout.addWidget(kit_container)


class AuthorTab(QScrollArea):
    """Class to display the author information in the main UI."""

    def __init__(self, author_data: AuthorData, parent: QWidget = None) -> None:
        """Scroll area that populates with incoming author information.

        Args:
            author_data: Data for the given author.
            parent: Widget to set as parent.
        """
        super(AuthorTab, self).__init__(parent)
        self.data = author_data
        self.setObjectName(self.data.name)
        self._build_ui()
        self._add_links()
        self._add_kits()
        self._sync_avatar()

    def _build_ui(self) -> None:
        """Builds the UI for the author tab."""
        self.base_widget = QWidget()
        self.base_layout = QVBoxLayout()
        self.base_layout.setAlignment(Qt.AlignCenter)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setAlignment(Qt.AlignTop)

        self.base_widget.setLayout(self.base_layout)
        self.setWidgetResizable(True)
        self.setWidget(self.base_widget)

        # Load avatar if it exists.
        self.avatar = Paths.AVATAR
        self.avatar_lbl = QLabel()
        self.avatar_lbl.setFixedSize(120, 100)
        self.avatar_pix = QPixmap(self.avatar.as_posix())
        # Load avatar image into the label.
        self._add_avatar()
        self.base_layout.addWidget(self.avatar_lbl, alignment=Qt.AlignCenter)
        # Add author name
        self.author_lbl = QLabel(self.data.name)
        self.base_layout.addWidget(self.author_lbl, alignment=Qt.AlignCenter)
        # Add links layout.
        self.links_layout = QHBoxLayout()
        self.base_layout.addLayout(self.links_layout)

    def _sync_avatar(self) -> None:
        """Syncs the local avatar with the database avatar."""
        # Fetch the avatar from the database and save it locally.
        self.thread = QThread()
        self.worker = AvatarWorker(self.data.name)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.on_avatar_finished)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_avatar_finished(self, avatar: QPixmap) -> None:
        """Sets the avatar pixmap to the label.

        Args:
            avatar: The avatar pixmap to set.
        """
        self.thread.quit()
        self.thread.wait()
        self.avatar_pix = avatar
        self._add_avatar()

    def _add_avatar(self) -> None:
        """Adds the author's avatar to the author tab."""
        avatar_pix = self.avatar_pix.scaledToHeight(100)
        self.avatar_lbl.setPixmap(avatar_pix)

    def _add_links(self) -> None:
        """Adds all links to the author tab as clickable."""
        for text, url in self.data.links.items():
            link_lbl = QLabel()
            link_lbl.setText(Text.lbl_link.format(text=text, link=url))
            link_lbl.setOpenExternalLinks(True)
            self.links_layout.addWidget(link_lbl)

    def _add_kits(self) -> None:
        """Iterate over the author's kits and add them to the UI."""
        for authors_kit in get_author_kits(self.data.name):
            # Add fold-able element for each kit
            folder = FoldContainer(name=authors_kit.label, version=authors_kit.version)
            # Since we are on the authors tab, don't show the author on each kit.
            kit_widget = KitWidget(authors_kit, show_author=False)
            folder.set_content(kit_widget)
            self.base_layout.addWidget(folder)


class InfoTab(QWidget):
    """Class to display the help information in the main UI."""

    def __init__(self) -> None:
        """Initialization of the Help Tab."""
        super(InfoTab, self).__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        """Builds the UI for the help tab."""
        self.base_layout = QVBoxLayout()
        self.base_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.base_layout)

        # Add about text
        self.about = QLabel()
        self.about.setObjectName("mkc-about")
        self.about.setText(Text.info_block)
        # Wrap the text
        self.about.setWordWrap(True)

        self.base_layout.addWidget(self.about)
