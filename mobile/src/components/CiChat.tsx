import React, { useState } from 'react';
import { View, FlatList, Text, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { InputBar } from './InputBar';

type Message = { id: string; text: string; from: 'user' | 'ci' };

export const CiChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);

  const send = (text: string) => {
    if (!text.trim()) return;
    setMessages(prev => [
      ...prev,
      { id: Date.now().toString(),       text,                          from: 'user' },
      { id: (Date.now() + 1).toString(), text: `[Ci]: processing — "${text}"`, from: 'ci' },
    ]);
  };

  return (
    <KeyboardAvoidingView style={s.wrap} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <FlatList
        data={messages} keyExtractor={m => m.id}
        renderItem={({ item }) => (
          <View style={[s.bubble, item.from === 'ci' ? s.ci : s.user]}>
            <Text style={s.txt}>{item.text}</Text>
          </View>
        )}
        contentContainerStyle={{ padding: 12 }}
      />
      <InputBar onSend={send} />
    </KeyboardAvoidingView>
  );
};

const s = StyleSheet.create({
  wrap:   { flex: 1, backgroundColor: '#0d0d0d' },
  bubble: { maxWidth: '80%', borderRadius: 12, padding: 10, marginVertical: 4 },
  user:   { backgroundColor: '#1a1a2e', alignSelf: 'flex-end' },
  ci:     { backgroundColor: '#16213e', alignSelf: 'flex-start' },
  txt:    { color: '#fff', fontSize: 14 },
});
