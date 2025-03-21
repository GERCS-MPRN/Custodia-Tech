package br.mp.mprn.gaeco.custodiatech.repository.auth;

import br.mp.mprn.gaeco.custodiatech.model.auth.UsuarioPerfil;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UsuarioPerfilRepository extends CrudRepository<UsuarioPerfil, Long> {

    List<UsuarioPerfil> findAllByUsuarioIdAndDeletadoFalse(Long idUsuario);

}
