import React from 'react'
import { useModal } from "../context/ModalContext";

import Modal from "../components/Modal"

const Transfer = ({closeModal}) => {
    const { isModalOpen, openModal  } = useModal();

  return (
    <Modal isOpen={isModalOpen} onClose={closeModal}>
    <div>Transfer</div>
    </Modal>
  )
}

export default Transfer