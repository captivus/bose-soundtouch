"""XML parsing and building utilities for the bose_soundtouch library."""

from __future__ import annotations

from xml.etree import ElementTree as ET

from bose_soundtouch.enums import ArtStatus, AudioMode, PlayStatus, SourceStatus
from bose_soundtouch.exceptions import ApiError, XmlParseError
from bose_soundtouch.models import (
    Art,
    AudioDspControls,
    Bass,
    BassCapabilities,
    Capabilities,
    Capability,
    Component,
    ContentItem,
    DeviceInfo,
    LevelControls,
    NetworkInfo,
    NowPlaying,
    Preset,
    Presets,
    SourceItem,
    Sources,
    SpeakerLevel,
    ToneControl,
    ToneControls,
    Volume,
    Zone,
    ZoneMember,
)


# XML declaration required by SoundTouch devices
# Note: No space before ?> - the device is picky about this
XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'


# ============ Helper Functions ============


def parse_xml(xml_string: str) -> ET.Element:
    """
    Parse XML string to Element.

    Args:
        xml_string: XML string to parse.

    Returns:
        Parsed XML Element.

    Raises:
        XmlParseError: If parsing fails.
    """
    try:
        return ET.fromstring(xml_string)
    except ET.ParseError as e:
        raise XmlParseError(f"Failed to parse XML: {e}") from e


def check_for_errors(root: ET.Element) -> None:
    """
    Check if response is an error and raise ApiError if so.

    Args:
        root: Parsed XML root element.

    Raises:
        ApiError: If the response contains an error.
    """
    if root.tag == "errors":
        device_id = root.get("deviceID")
        error_elem = root.find("error")
        if error_elem is not None:
            raise ApiError(
                message=error_elem.text or "Unknown error",
                device_id=device_id,
                error_code=_get_int(error_elem.get("value", "0")),
                error_name=error_elem.get("name"),
                severity=error_elem.get("severity"),
            )
        raise ApiError(message="Unknown error", device_id=device_id)

    # Handle simple error format
    if root.tag == "error":
        raise ApiError(message=root.text or "Unknown error")


def _get_text(element: ET.Element | None, default: str = "") -> str:
    """Get text content of element or default."""
    if element is None or element.text is None:
        return default
    return element.text.strip()


def _get_bool(text: str) -> bool:
    """Parse boolean from XML text."""
    return text.lower() == "true"


def _get_int(text: str, default: int = 0) -> int:
    """Parse integer from XML text."""
    try:
        return int(text)
    except (ValueError, TypeError):
        return default


def _escape_xml(text: str) -> str:
    """Escape special XML characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


# ============ Content Item Parser ============


def _parse_content_item(elem: ET.Element | None) -> ContentItem | None:
    """Parse a ContentItem element."""
    if elem is None:
        return None

    item_name_elem = elem.find("itemName")

    return ContentItem(
        source=elem.get("source", ""),
        location=elem.get("location"),
        source_account=elem.get("sourceAccount"),
        is_presetable=_get_bool(elem.get("isPresetable", "false")),
        item_name=_get_text(item_name_elem) if item_name_elem is not None else None,
    )


# ============ Response Parsers ============


def parse_device_info(root: ET.Element) -> DeviceInfo:
    """
    Parse /info response.

    Args:
        root: Parsed XML root element.

    Returns:
        DeviceInfo model.
    """
    components = []
    components_elem = root.find("components")
    if components_elem is not None:
        for comp_elem in components_elem.findall("component"):
            components.append(
                Component(
                    category=_get_text(comp_elem.find("componentCategory")),
                    software_version=_get_text(comp_elem.find("softwareVersion")),
                    serial_number=_get_text(comp_elem.find("serialNumber")) or None,
                )
            )

    network_info = []
    for net_elem in root.findall("networkInfo"):
        network_info.append(
            NetworkInfo(
                type=net_elem.get("type", ""),
                mac_address=_get_text(net_elem.find("macAddress")),
                ip_address=_get_text(net_elem.find("ipAddress")),
            )
        )

    return DeviceInfo(
        device_id=root.get("deviceID", ""),
        name=_get_text(root.find("name")),
        type=_get_text(root.find("type")),
        account_uuid=_get_text(root.find("margeAccountUUID")) or None,
        marge_url=_get_text(root.find("margeURL")) or None,
        components=components,
        network_info=network_info,
    )


def parse_now_playing(root: ET.Element) -> NowPlaying:
    """
    Parse /now_playing or /trackInfo response.

    Args:
        root: Parsed XML root element.

    Returns:
        NowPlaying model.
    """
    art_elem = root.find("art")
    art = None
    if art_elem is not None:
        art_status_str = art_elem.get("artImageStatus", "INVALID")
        try:
            art_status = ArtStatus(art_status_str)
        except ValueError:
            art_status = ArtStatus.INVALID
        art = Art(
            url=_get_text(art_elem) or None,
            status=art_status,
        )

    play_status_str = _get_text(root.find("playStatus"), "INVALID_PLAY_STATUS")
    try:
        play_status = PlayStatus(play_status_str)
    except ValueError:
        play_status = PlayStatus.INVALID_PLAY_STATUS

    return NowPlaying(
        device_id=root.get("deviceID", ""),
        source=root.get("source", ""),
        content_item=_parse_content_item(root.find("ContentItem")),
        track=_get_text(root.find("track")) or None,
        artist=_get_text(root.find("artist")) or None,
        album=_get_text(root.find("album")) or None,
        station_name=_get_text(root.find("stationName")) or None,
        art=art,
        play_status=play_status,
        description=_get_text(root.find("description")) or None,
        station_location=_get_text(root.find("stationLocation")) or None,
    )


def parse_sources(root: ET.Element) -> Sources:
    """
    Parse /sources response.

    Args:
        root: Parsed XML root element.

    Returns:
        Sources model.
    """
    items = []
    for item_elem in root.findall("sourceItem"):
        status_str = item_elem.get("status", "UNAVAILABLE")
        try:
            status = SourceStatus(status_str)
        except ValueError:
            status = SourceStatus.UNAVAILABLE

        items.append(
            SourceItem(
                source=item_elem.get("source", ""),
                source_account=item_elem.get("sourceAccount"),
                status=status,
                display_name=_get_text(item_elem) or None,
            )
        )

    return Sources(
        device_id=root.get("deviceID", ""),
        items=items,
    )


def parse_volume(root: ET.Element) -> Volume:
    """
    Parse /volume response.

    Args:
        root: Parsed XML root element.

    Returns:
        Volume model.
    """
    return Volume(
        device_id=root.get("deviceID", ""),
        target_volume=_get_int(_get_text(root.find("targetvolume"))),
        actual_volume=_get_int(_get_text(root.find("actualvolume"))),
        mute_enabled=_get_bool(_get_text(root.find("muteenabled"), "false")),
    )


def parse_bass(root: ET.Element) -> Bass:
    """
    Parse /bass response.

    Args:
        root: Parsed XML root element.

    Returns:
        Bass model.
    """
    return Bass(
        device_id=root.get("deviceID", ""),
        target_bass=_get_int(_get_text(root.find("targetbass"))),
        actual_bass=_get_int(_get_text(root.find("actualbass"))),
    )


def parse_bass_capabilities(root: ET.Element) -> BassCapabilities:
    """
    Parse /bassCapabilities response.

    Args:
        root: Parsed XML root element.

    Returns:
        BassCapabilities model.
    """
    return BassCapabilities(
        device_id=root.get("deviceID", ""),
        bass_available=_get_bool(_get_text(root.find("bassAvailable"), "false")),
        bass_min=_get_int(_get_text(root.find("bassMin"))),
        bass_max=_get_int(_get_text(root.find("bassMax"))),
        bass_default=_get_int(_get_text(root.find("bassDefault"))),
    )


def parse_presets(root: ET.Element) -> Presets:
    """
    Parse /presets response.

    Args:
        root: Parsed XML root element.

    Returns:
        Presets model.
    """
    items = []
    for preset_elem in root.findall("preset"):
        preset_id = _get_int(preset_elem.get("id", "0"))
        created_on_str = preset_elem.get("createdOn")
        updated_on_str = preset_elem.get("updatedOn")

        items.append(
            Preset(
                id=preset_id,
                content_item=_parse_content_item(preset_elem.find("ContentItem")),
                created_on=_get_int(created_on_str) if created_on_str else None,
                updated_on=_get_int(updated_on_str) if updated_on_str else None,
            )
        )

    return Presets(items=items)


def parse_zone(root: ET.Element) -> Zone:
    """
    Parse /getZone response.

    Args:
        root: Parsed XML root element.

    Returns:
        Zone model.
    """
    members = []
    for member_elem in root.findall("member"):
        mac_address = _get_text(member_elem).strip('"')
        ip_address = member_elem.get("ipaddress", "")
        members.append(
            ZoneMember(
                mac_address=mac_address,
                ip_address=ip_address,
            )
        )

    return Zone(
        master_mac=root.get("master"),
        members=members,
    )


def parse_capabilities(root: ET.Element) -> Capabilities:
    """
    Parse /capabilities response.

    Args:
        root: Parsed XML root element.

    Returns:
        Capabilities model.
    """
    items = []
    for cap_elem in root.findall("capability"):
        items.append(
            Capability(
                name=cap_elem.get("name", ""),
                url=cap_elem.get("url", ""),
                info=cap_elem.get("info"),
            )
        )

    return Capabilities(
        device_id=root.get("deviceID", ""),
        items=items,
    )


def parse_audio_dsp_controls(root: ET.Element) -> AudioDspControls:
    """
    Parse /audiodspcontrols response.

    Args:
        root: Parsed XML root element.

    Returns:
        AudioDspControls model.
    """
    audio_mode_str = root.get("audiomode", "AUDIO_MODE_NORMAL")
    try:
        audio_mode = AudioMode(audio_mode_str)
    except ValueError:
        audio_mode = AudioMode.NORMAL

    supported_modes_str = root.get("supportedaudiomodes", "")
    supported_modes = []
    if supported_modes_str:
        for mode_str in supported_modes_str.split("|"):
            try:
                supported_modes.append(AudioMode(mode_str))
            except ValueError:
                pass

    return AudioDspControls(
        audio_mode=audio_mode,
        video_sync_audio_delay=_get_int(root.get("videosyncaudiodelay", "0")),
        supported_audio_modes=supported_modes,
    )


def parse_tone_controls(root: ET.Element) -> ToneControls:
    """
    Parse /audioproducttonecontrols response.

    Args:
        root: Parsed XML root element.

    Returns:
        ToneControls model.
    """
    bass_elem = root.find("bass")
    bass = None
    if bass_elem is not None:
        bass = ToneControl(
            value=_get_int(bass_elem.get("value", "0")),
            min_value=_get_int(bass_elem.get("minValue", "0")),
            max_value=_get_int(bass_elem.get("maxValue", "0")),
            step=_get_int(bass_elem.get("step", "1")),
        )

    treble_elem = root.find("treble")
    treble = None
    if treble_elem is not None:
        treble = ToneControl(
            value=_get_int(treble_elem.get("value", "0")),
            min_value=_get_int(treble_elem.get("minValue", "0")),
            max_value=_get_int(treble_elem.get("maxValue", "0")),
            step=_get_int(treble_elem.get("step", "1")),
        )

    return ToneControls(
        bass=bass,
        treble=treble,
    )


def parse_level_controls(root: ET.Element) -> LevelControls:
    """
    Parse /audioproductlevelcontrols response.

    Args:
        root: Parsed XML root element.

    Returns:
        LevelControls model.
    """
    front_elem = root.find("frontCenterSpeakerLevel")
    front_center = None
    if front_elem is not None:
        front_center = SpeakerLevel(
            value=_get_int(front_elem.get("value", "0")),
            min_value=_get_int(front_elem.get("minValue", "0")),
            max_value=_get_int(front_elem.get("maxValue", "0")),
            step=_get_int(front_elem.get("step", "1")),
        )

    rear_elem = root.find("rearSurroundSpeakersLevel")
    rear_surround = None
    if rear_elem is not None:
        rear_surround = SpeakerLevel(
            value=_get_int(rear_elem.get("value", "0")),
            min_value=_get_int(rear_elem.get("minValue", "0")),
            max_value=_get_int(rear_elem.get("maxValue", "0")),
            step=_get_int(rear_elem.get("step", "1")),
        )

    return LevelControls(
        front_center=front_center,
        rear_surround=rear_surround,
    )


# ============ XML Builders ============


def build_key_xml(*, key: str, state: str, sender: str) -> str:
    """
    Build XML for /key POST.

    Args:
        key: Key value (e.g., "PLAY", "PAUSE").
        state: Key state ("press" or "release").
        sender: Sender identifier.

    Returns:
        XML string.
    """
    return f'{XML_DECLARATION}<key state="{state}" sender="{_escape_xml(sender)}">{key}</key>'


def build_volume_xml(*, volume: int | None, mute: bool | None) -> str:
    """
    Build XML for /volume POST.

    Args:
        volume: Volume level (0-100), or None to not change.
        mute: Mute state, or None to not change.

    Returns:
        XML string.
    """
    parts = [XML_DECLARATION, "<volume>"]
    if volume is not None:
        parts.append(str(volume))
    if mute is not None:
        mute_str = "true" if mute else "false"
        parts.append(f"<muteenabled>{mute_str}</muteenabled>")
    parts.append("</volume>")
    return "".join(parts)


def build_bass_xml(*, bass: int) -> str:
    """
    Build XML for /bass POST.

    Args:
        bass: Bass level.

    Returns:
        XML string.
    """
    return f"{XML_DECLARATION}<bass>{bass}</bass>"


def build_name_xml(*, name: str) -> str:
    """
    Build XML for /name POST.

    Args:
        name: New device name.

    Returns:
        XML string.
    """
    return f"{XML_DECLARATION}<name>{_escape_xml(name)}</name>"


def build_select_xml(*, content_item: ContentItem) -> str:
    """
    Build XML for /select POST.

    Args:
        content_item: Content item to select.

    Returns:
        XML string.
    """
    attrs = [f'source="{_escape_xml(content_item.source)}"']
    if content_item.source_account:
        attrs.append(f'sourceAccount="{_escape_xml(content_item.source_account)}"')
    if content_item.location:
        attrs.append(f'location="{_escape_xml(content_item.location)}"')

    attrs_str = " ".join(attrs)

    if content_item.item_name:
        return f"{XML_DECLARATION}<ContentItem {attrs_str}><itemName>{_escape_xml(content_item.item_name)}</itemName></ContentItem>"
    return f"{XML_DECLARATION}<ContentItem {attrs_str}></ContentItem>"


def build_zone_xml(
    *,
    master_mac: str,
    members: list[ZoneMember],
    sender_ip: str | None,
) -> str:
    """
    Build XML for /setZone POST.

    Args:
        master_mac: MAC address of the zone master.
        members: List of zone members.
        sender_ip: IP address of the sender.

    Returns:
        XML string.
    """
    parts = [XML_DECLARATION, f'<zone master="{master_mac}"']
    if sender_ip:
        parts.append(f' senderIPAddress="{sender_ip}"')
    parts.append(">")

    for member in members:
        parts.append(
            f'<member ipaddress="{member.ip_address}">{member.mac_address}</member>'
        )

    parts.append("</zone>")
    return "".join(parts)


def build_zone_member_xml(*, master_mac: str, members: list[ZoneMember]) -> str:
    """
    Build XML for /addZoneSlave and /removeZoneSlave POST.

    Args:
        master_mac: MAC address of the zone master.
        members: List of zone members to add/remove.

    Returns:
        XML string.
    """
    parts = [XML_DECLARATION, f'<zone master="{master_mac}">']

    for member in members:
        parts.append(
            f'<member ipaddress="{member.ip_address}">{member.mac_address}</member>'
        )

    parts.append("</zone>")
    return "".join(parts)


def build_audio_dsp_xml(
    *,
    audio_mode: AudioMode | None,
    delay: int | None,
) -> str:
    """
    Build XML for /audiodspcontrols POST.

    Args:
        audio_mode: Audio mode to set, or None to not change.
        delay: Video sync audio delay, or None to not change.

    Returns:
        XML string.
    """
    attrs = []
    if audio_mode is not None:
        attrs.append(f'audiomode="{audio_mode.value}"')
    if delay is not None:
        attrs.append(f'videosyncaudiodelay="{delay}"')

    attrs_str = " ".join(attrs)
    return f"{XML_DECLARATION}<audiodspcontrols {attrs_str}/>"


def build_tone_controls_xml(*, bass: int | None, treble: int | None) -> str:
    """
    Build XML for /audioproducttonecontrols POST.

    Args:
        bass: Bass value to set, or None to not change.
        treble: Treble value to set, or None to not change.

    Returns:
        XML string.
    """
    parts = [XML_DECLARATION, "<audioproducttonecontrols>"]
    if bass is not None:
        parts.append(f'<bass value="{bass}" />')
    if treble is not None:
        parts.append(f'<treble value="{treble}" />')
    parts.append("</audioproducttonecontrols>")
    return "".join(parts)


def build_level_controls_xml(
    *,
    front_center: int | None,
    rear_surround: int | None,
) -> str:
    """
    Build XML for /audioproductlevelcontrols POST.

    Args:
        front_center: Front center speaker level, or None to not change.
        rear_surround: Rear surround speakers level, or None to not change.

    Returns:
        XML string.
    """
    parts = [XML_DECLARATION, "<audioproductlevelcontrols>"]
    if front_center is not None:
        parts.append(f'<frontCenterSpeakerLevel value="{front_center}" />')
    if rear_surround is not None:
        parts.append(f'<rearSurroundSpeakersLevel value="{rear_surround}" />')
    parts.append("</audioproductlevelcontrols>")
    return "".join(parts)
