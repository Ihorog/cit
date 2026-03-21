import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet, Modal } from 'react-native';

type Props = { onSend: (text: string) => void; onImagePick?: () => void };

const PLUS_MENU = ['image', 'file', 'event', 'note'] as const;

export const InputBar: React.FC<Props> = ({ onSend, onImagePick }) => {
  const [text, setText] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <View style={s.bar}>
      <TouchableOpacity onPress={() => setMenuOpen(true)} style={s.icon}>
        <Text style={s.iconTxt}>+</Text>
      </TouchableOpacity>
      <TextInput
        style={s.input} value={text} onChangeText={setText}
        placeholder="..." placeholderTextColor="#555"
        returnKeyType="send"
        onSubmitEditing={() => { onSend(text); setText(''); }}
      />
      <TouchableOpacity onPress={() => {/* voice input stub */}} style={s.icon}>
        <Text style={s.iconTxt}>🎤</Text>
      </TouchableOpacity>

      <Modal visible={menuOpen} transparent animationType="fade">
        <TouchableOpacity style={s.overlay} onPress={() => setMenuOpen(false)}>
          <View style={s.menu}>
            {PLUS_MENU.map(item => (
              <TouchableOpacity key={item} style={s.menuItem}
                onPress={() => { if (item === 'image') onImagePick?.(); setMenuOpen(false); }}>
                <Text style={s.menuTxt}>{item}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
};

const s = StyleSheet.create({
  bar:     { flexDirection: 'row', alignItems: 'center', padding: 8, backgroundColor: '#111' },
  input:   { flex: 1, color: '#fff', paddingHorizontal: 12, paddingVertical: 8,
             backgroundColor: '#1e1e1e', borderRadius: 20, marginHorizontal: 4 },
  icon:    { padding: 8 },
  iconTxt: { color: '#fff', fontSize: 20 },
  overlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  menu:    { backgroundColor: '#1a1a2e', borderRadius: 12, margin: 16, padding: 12 },
  menuItem:{ paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#333' },
  menuTxt: { color: '#fff', fontSize: 16, textTransform: 'capitalize' },
});
