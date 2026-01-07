"""Shared test fixtures for bose_soundtouch tests."""

import pytest


# ============ Sample XML Responses ============


@pytest.fixture
def info_xml() -> str:
    """Sample /info response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<info deviceID="AABBCCDDEEFF">
    <name>Living Room</name>
    <type>SoundTouch 10</type>
    <margeAccountUUID>abc123</margeAccountUUID>
    <components>
        <component>
            <componentCategory>SCM</componentCategory>
            <softwareVersion>1.0.0</softwareVersion>
            <serialNumber>SN123456</serialNumber>
        </component>
    </components>
    <margeURL>https://example.bose.com</margeURL>
    <networkInfo type="WIFI">
        <macAddress>AABBCCDDEEFF</macAddress>
        <ipAddress>192.168.1.100</ipAddress>
    </networkInfo>
</info>"""


@pytest.fixture
def now_playing_xml() -> str:
    """Sample /now_playing response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<nowPlaying deviceID="AABBCCDDEEFF" source="SPOTIFY">
    <ContentItem source="SPOTIFY" location="spotify:track:123" sourceAccount="user@example.com" isPresetable="true">
        <itemName>My Playlist</itemName>
    </ContentItem>
    <track>Test Track</track>
    <artist>Test Artist</artist>
    <album>Test Album</album>
    <stationName></stationName>
    <art artImageStatus="IMAGE_PRESENT">https://example.com/art.jpg</art>
    <playStatus>PLAY_STATE</playStatus>
    <description>A great song</description>
    <stationLocation></stationLocation>
</nowPlaying>"""


@pytest.fixture
def sources_xml() -> str:
    """Sample /sources response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<sources deviceID="AABBCCDDEEFF">
    <sourceItem source="AUX" sourceAccount="AUX" status="READY">AUX Input</sourceItem>
    <sourceItem source="BLUETOOTH" sourceAccount="" status="READY">Bluetooth</sourceItem>
    <sourceItem source="SPOTIFY" sourceAccount="user@example.com" status="UNAVAILABLE">Spotify</sourceItem>
</sources>"""


@pytest.fixture
def volume_xml() -> str:
    """Sample /volume response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<volume deviceID="AABBCCDDEEFF">
    <targetvolume>50</targetvolume>
    <actualvolume>50</actualvolume>
    <muteenabled>false</muteenabled>
</volume>"""


@pytest.fixture
def bass_xml() -> str:
    """Sample /bass response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<bass deviceID="AABBCCDDEEFF">
    <targetbass>0</targetbass>
    <actualbass>0</actualbass>
</bass>"""


@pytest.fixture
def bass_capabilities_xml() -> str:
    """Sample /bassCapabilities response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<bassCapabilities deviceID="AABBCCDDEEFF">
    <bassAvailable>true</bassAvailable>
    <bassMin>-9</bassMin>
    <bassMax>9</bassMax>
    <bassDefault>0</bassDefault>
</bassCapabilities>"""


@pytest.fixture
def presets_xml() -> str:
    """Sample /presets response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<presets>
    <preset id="1" createdOn="1234567890" updatedOn="1234567890">
        <ContentItem source="TUNEIN" location="station123" sourceAccount="" isPresetable="true">
            <itemName>NPR News</itemName>
        </ContentItem>
    </preset>
    <preset id="2">
        <ContentItem source="SPOTIFY" location="playlist456" sourceAccount="user@example.com" isPresetable="true">
            <itemName>My Playlist</itemName>
        </ContentItem>
    </preset>
</presets>"""


@pytest.fixture
def zone_xml() -> str:
    """Sample /getZone response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<zone master="AABBCCDDEEFF">
    <member ipaddress="192.168.1.100">"AABBCCDDEEFF"</member>
    <member ipaddress="192.168.1.101">"112233445566"</member>
</zone>"""


@pytest.fixture
def capabilities_xml() -> str:
    """Sample /capabilities response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<capabilities deviceID="AABBCCDDEEFF">
    <capability name="audiodspcontrols" url="/audiodspcontrols" info=""/>
    <capability name="audioproducttonecontrols" url="/audioproducttonecontrols" info="bass,treble"/>
</capabilities>"""


@pytest.fixture
def audio_dsp_controls_xml() -> str:
    """Sample /audiodspcontrols response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<audiodspcontrols audiomode="AUDIO_MODE_NORMAL" videosyncaudiodelay="0" supportedaudiomodes="AUDIO_MODE_NORMAL|AUDIO_MODE_DIALOG|AUDIO_MODE_NIGHT"/>"""


@pytest.fixture
def tone_controls_xml() -> str:
    """Sample /audioproducttonecontrols response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<audioproducttonecontrols>
    <bass value="0" minValue="-10" maxValue="10" step="1"/>
    <treble value="0" minValue="-10" maxValue="10" step="1"/>
</audioproducttonecontrols>"""


@pytest.fixture
def level_controls_xml() -> str:
    """Sample /audioproductlevelcontrols response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<audioproductlevelcontrols>
    <frontCenterSpeakerLevel value="0" minValue="-10" maxValue="10" step="1"/>
    <rearSurroundSpeakersLevel value="0" minValue="-10" maxValue="10" step="1"/>
</audioproductlevelcontrols>"""


@pytest.fixture
def error_xml() -> str:
    """Sample error response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<errors deviceID="AABBCCDDEEFF">
    <error value="1019" name="CLIENT_XML_ERROR" severity="Unknown">Invalid request</error>
</errors>"""


@pytest.fixture
def status_xml() -> str:
    """Sample status response XML."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<status>/volume</status>"""
